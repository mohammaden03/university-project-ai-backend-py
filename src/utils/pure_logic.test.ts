import test from 'node:test';
import assert from 'node:assert/strict';
import {
  normalizePersianArabicText,
  calculateCER,
  calculateWER,
  reciprocalRankFusion,
  buildSourceCitations,
  SearchResultItem,
} from './pure_logic';

test('normalizePersianArabicText: converts Arabic kaf and yeh to Persian characters', () => {
  const input = 'كتاب الحاوي في الطب';
  const output = normalizePersianArabicText(input);
  assert.equal(output, 'کتاب الحاوی فی الطب');
});

test('normalizePersianArabicText: strips tatweel and tashkeel diacritics', () => {
  const input = 'بِـــــسْمِ اللهِ الرَّحْمَـــــنِ الرَّحِيمِ';
  const output = normalizePersianArabicText(input);
  assert.equal(output, 'بسم الله الرحمن الرحیم');
});

test('calculateCER: returns 0 for identical strings and calculates correct error percentage', () => {
  const ref = 'بسم الله الرحمن الرحیم';
  const hyp = 'بسم الله الرحمن الرحیم';
  assert.equal(calculateCER(ref, hyp), 0);

  // Missing one word/character
  const hypErr = 'بسم الله الرحیم'; // missing 'الرحمن '
  const cer = calculateCER(ref, hypErr);
  assert.ok(cer > 0 && cer < 1);
});

test('calculateWER: computes word error rate on Persian text', () => {
  const ref = 'شیخ الرئیس ابو علی سینا';
  const hyp = 'شیخ ابو علی سینا'; // 1 deletion out of 5 words
  const wer = calculateWER(ref, hyp);
  assert.equal(wer, 0.2);
});

test('reciprocalRankFusion: boosts documents present in both lexical and semantic channels to hybrid', () => {
  const lexical: SearchResultItem[] = [
    {
      id: 'doc-1',
      text: 'قانون فی الطب ابن سینا',
      manuscriptTitle: 'نسخه خطی ملک',
      pageNumber: 1,
      relevanceScore: 0.9,
      matchType: 'lexical',
    },
    {
      id: 'doc-2',
      text: 'داروشناسی بیرونی',
      manuscriptTitle: 'الصیدنه',
      pageNumber: 12,
      relevanceScore: 0.7,
      matchType: 'lexical',
    },
  ];

  const semantic: SearchResultItem[] = [
    {
      id: 'doc-2',
      text: 'داروشناسی بیرونی',
      manuscriptTitle: 'الصیدنه',
      pageNumber: 12,
      relevanceScore: 0.95,
      matchType: 'semantic',
    },
    {
      id: 'doc-3',
      text: 'الحاوی رازی',
      manuscriptTitle: 'نسخه ایاصوفیا',
      pageNumber: 8,
      relevanceScore: 0.8,
      matchType: 'semantic',
    },
  ];

  const fused = reciprocalRankFusion(lexical, semantic);
  assert.equal(fused.length, 3);
  // doc-2 matched in both lists -> becomes hybrid and ranks top
  assert.equal(fused[0].id, 'doc-2');
  assert.equal(fused[0].matchType, 'hybrid');
});

test('buildSourceCitations: preserves genuine book, author, and page references', () => {
  const items: SearchResultItem[] = [
    {
      id: 'res-101',
      text: 'الطب علم يتعرف منه احوال بدن الانسان',
      bookTitle: 'قانون فی الطب',
      authorName: 'ابن سینا',
      manuscriptTitle: 'نسخه کهن ملک',
      pageNumber: 1,
      relevanceScore: 0.95,
      matchType: 'hybrid',
    },
  ];

  const citations = buildSourceCitations(items);
  assert.equal(citations.length, 1);
  assert.equal(citations[0].sourceId, 'SRC-1');
  assert.equal(citations[0].bookTitle, 'قانون فی الطب');
  assert.equal(citations[0].authorName, 'ابن سینا');
  assert.equal(citations[0].pageNumber, 1);
});
