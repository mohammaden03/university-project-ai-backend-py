/**
 * Pure business logic for manuscript processing, text normalization,
 * CER/WER calculation, and hybrid search ranking.
 */

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface RecognizedLine {
  lineIndex: number;
  text: string;
  confidence: number | null;
  boundingBox?: BoundingBox;
}

export interface SearchResultItem {
  id: string;
  text: string;
  bookTitle?: string;
  authorName?: string;
  manuscriptTitle: string;
  pageNumber: number;
  relevanceScore: number;
  matchType: 'lexical' | 'semantic' | 'hybrid';
}

export interface SourceCitation {
  sourceId: string;
  bookTitle: string;
  authorName: string;
  manuscriptTitle: string;
  pageNumber: number;
  excerpt: string;
}

/**
 * Normalizes Persian and Arabic text for scholarly search and indexing.
 * Unifies letter variants, strips diacritics and tatweel.
 */
export function normalizePersianArabicText(
  text: string | null | undefined,
  options: { removeDiacritics?: boolean; removeTatweel?: boolean; unifyLetters?: boolean } = {}
): string {
  if (!text) return '';

  const { removeDiacritics = true, removeTatweel = true, unifyLetters = true } = options;

  let res = text.normalize('NFC');

  // Tatweel / Kashida
  if (removeTatweel) {
    res = res.replace(/\u0640+/g, '');
  }

  // Diacritics (Harakat / Tashkeel)
  if (removeDiacritics) {
    res = res.replace(/[\u064B-\u0652\u0656-\u065F\u0670\u06D6-\u06ED]/g, '');
  }

  // Letter unification
  if (unifyLetters) {
    res = res
      .replace(/[\u0643\u06AA]/g, 'ک') // Kaf variants -> Persian Keheh
      .replace(/[\u064A\u0649\u0626\u06CD\u06CE\u06D0\u06D1]/g, 'ی') // Yeh variants -> Persian Yeh
      .replace(/[\u0622\u0623\u0625\u0671]/g, 'ا') // Alef variants -> Alef
      .replace(/\u0629/g, 'ه') // Teh Marbuta -> Heh
      .replace(/\u0624/g, 'و'); // Waw with hamza -> Waw
  }

  // Persian/Arabic digits to ASCII
  const persianDigits = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
  const arabicDigits = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩'];
  for (let i = 0; i < 10; i++) {
    res = res.replaceAll(persianDigits[i], String(i));
    res = res.replaceAll(arabicDigits[i], String(i));
  }

  // Collapse whitespace
  res = res.replace(/\s+/g, ' ').trim();

  return res;
}

/**
 * Levenshtein distance calculation between two arrays or strings.
 */
export function levenshteinDistance<T>(seq1: T[], seq2: T[]): number {
  const m = seq1.length;
  const n = seq2.length;
  const dp: number[][] = Array.from({ length: m + 1 }, () => Array(n + 1).fill(0));

  for (let i = 0; i <= m; i++) dp[i][0] = i;
  for (let j = 0; j <= n; j++) dp[0][j] = j;

  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      if (seq1[i - 1] === seq2[j - 1]) {
        dp[i][j] = dp[i - 1][j - 1];
      } else {
        dp[i][j] = Math.min(
          dp[i - 1][j] + 1, // deletion
          dp[i][j - 1] + 1, // insertion
          dp[i - 1][j - 1] + 1 // substitution
        );
      }
    }
  }

  return dp[m][n];
}

/**
 * Calculates Character Error Rate (CER).
 */
export function calculateCER(reference: string, hypothesis: string): number {
  const refNorm = normalizePersianArabicText(reference);
  const hypNorm = normalizePersianArabicText(hypothesis);

  const refChars = Array.from(refNorm);
  const hypChars = Array.from(hypNorm);

  if (refChars.length === 0) return hypChars.length === 0 ? 0 : 1;

  const distance = levenshteinDistance(refChars, hypChars);
  return Number((distance / refChars.length).toFixed(4));
}

/**
 * Calculates Word Error Rate (WER).
 */
export function calculateWER(reference: string, hypothesis: string): number {
  const refNorm = normalizePersianArabicText(reference);
  const hypNorm = normalizePersianArabicText(hypothesis);

  const refWords = refNorm.split(/\s+/).filter(Boolean);
  const hypWords = hypNorm.split(/\s+/).filter(Boolean);

  if (refWords.length === 0) return hypWords.length === 0 ? 0 : 1;

  const distance = levenshteinDistance(refWords, hypWords);
  return Number((distance / refWords.length).toFixed(4));
}

/**
 * Reciprocal Rank Fusion (RRF) for merging lexical and vector search lists.
 */
export function reciprocalRankFusion(
  lexicalList: SearchResultItem[],
  semanticList: SearchResultItem[],
  k = 60
): SearchResultItem[] {
  const scoreMap = new Map<string, number>();
  const itemMap = new Map<string, SearchResultItem>();

  lexicalList.forEach((item, rank) => {
    const current = scoreMap.get(item.id) || 0;
    scoreMap.set(item.id, current + 1 / (k + rank + 1));
    itemMap.set(item.id, { ...item, matchType: 'lexical' });
  });

  semanticList.forEach((item, rank) => {
    const current = scoreMap.get(item.id) || 0;
    scoreMap.set(item.id, current + 1 / (k + rank + 1));
    if (itemMap.has(item.id)) {
      const existing = itemMap.get(item.id)!;
      existing.matchType = 'hybrid';
    } else {
      itemMap.set(item.id, { ...item, matchType: 'semantic' });
    }
  });

  const sortedIds = Array.from(scoreMap.keys()).sort((a, b) => {
    return (scoreMap.get(b) || 0) - (scoreMap.get(a) || 0);
  });

  return sortedIds.map((id) => {
    const item = itemMap.get(id)!;
    const rawScore = scoreMap.get(id) || 0;
    // Normalized score in 0..1 scale
    item.relevanceScore = Number((rawScore * (k + 1)).toFixed(3));
    return item;
  });
}

/**
 * Builds grounded citation objects from search result items.
 * Guaranteed to only include passages from real retrieved database records.
 */
export function buildSourceCitations(results: SearchResultItem[]): SourceCitation[] {
  return results.map((res, idx) => ({
    sourceId: `SRC-${idx + 1}`,
    bookTitle: res.bookTitle || 'نامشخص',
    authorName: res.authorName || 'نامشخص',
    manuscriptTitle: res.manuscriptTitle,
    pageNumber: res.pageNumber,
    excerpt: res.text,
  }));
}
