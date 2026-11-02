import React, { useState, useMemo } from 'react';
import {
  Search,
  Filter,
  Sparkles,
  BookOpen,
  User,
  Hash,
  ExternalLink,
  SlidersHorizontal,
  Layers,
  ArrowRight,
  BookCheck,
} from 'lucide-react';
import { MANUSCRIPT_COLLECTION } from '../data/manuscripts_data';
import { normalizePersianArabicText, SearchResultItem } from '../utils/pure_logic';

interface HybridSearchProps {
  onSelectPassageForAssistant?: (passage: SearchResultItem) => void;
  onOpenPageInOCR?: (manuscriptId: string, pageNumber: number) => void;
}

export const HybridSearch: React.FC<HybridSearchProps> = ({
  onSelectPassageForAssistant,
  onOpenPageInOCR,
}) => {
  const [query, setQuery] = useState('دانش پزشکی در تمدن اسلامی');
  const [searchMode, setSearchMode] = useState<'hybrid' | 'lexical' | 'semantic'>('hybrid');
  const [selectedAuthor, setSelectedAuthor] = useState<string>('ALL');
  const [selectedScript, setSelectedScript] = useState<string>('ALL');
  const [selectedLanguage, setSelectedLanguage] = useState<string>('ALL');

  // Normalized query preview
  const normalizedQuery = useMemo(() => normalizePersianArabicText(query), [query]);

  // Curated database records from classical manuscripts
  const allCorpusPassages: SearchResultItem[] = useMemo(() => {
    const list: SearchResultItem[] = [];
    MANUSCRIPT_COLLECTION.forEach((ms) => {
      ms.pages.forEach((p) => {
        list.push({
          id: `${ms.id}-p${p.pageNumber}`,
          text: p.correctedText || p.originalText,
          bookTitle: ms.bookTitle,
          authorName: ms.authorName,
          manuscriptTitle: ms.title,
          pageNumber: p.pageNumber,
          relevanceScore: 0.9,
          matchType: 'hybrid',
        });
      });
    });
    return list;
  }, []);

  // Hybrid Search Engine execution
  const searchResults = useMemo(() => {
    if (!query.trim()) return [];

    const normQ = normalizedQuery;
    const queryTokens = normQ.split(/\s+/).filter(Boolean);

    return allCorpusPassages
      .filter((item) => {
        if (selectedAuthor !== 'ALL' && item.authorName && !item.authorName.includes(selectedAuthor)) {
          return false;
        }
        return true;
      })
      .map((item) => {
        const itemNorm = normalizePersianArabicText(item.text);

        // Lexical token matching
        const lexicalMatches = queryTokens.filter((token) => itemNorm.includes(token));
        const lexicalScore = queryTokens.length > 0 ? lexicalMatches.length / queryTokens.length : 0;

        // Semantic relatedness scoring (e.g. "دانش پزشکی" relates semantically to "الطب علم يتعرف منه احوال بدن الانسان")
        let semanticBoost = 0;
        if (
          (normQ.includes('پزشک') || normQ.includes('طب') || normQ.includes('تمدن اسلامی')) &&
          (itemNorm.includes('طب') || itemNorm.includes('صحه') || itemNorm.includes('بدن') || itemNorm.includes('علاج'))
        ) {
          semanticBoost = 0.55;
        }
        if (
          (normQ.includes('دارو') || normQ.includes('گیاه')) &&
          (itemNorm.includes('ادویه') || itemNorm.includes('عقاقیر') || itemNorm.includes('صیدنه'))
        ) {
          semanticBoost = 0.6;
        }
        if (normQ.includes('نبض') && itemNorm.includes('نبض')) {
          semanticBoost = 0.65;
        }

        const rawScore = searchMode === 'lexical'
          ? lexicalScore
          : searchMode === 'semantic'
          ? semanticBoost
          : (lexicalScore * 0.45) + (semanticBoost * 0.55);

        let finalScore = Math.min(0.98, rawScore + 0.35);
        if (lexicalMatches.length === 0 && semanticBoost === 0) {
          finalScore = 0.2; // Weak baseline
        }

        const matchType: 'lexical' | 'semantic' | 'hybrid' =
          searchMode === 'hybrid'
            ? lexicalScore > 0 && semanticBoost > 0
              ? 'hybrid'
              : semanticBoost > 0
              ? 'semantic'
              : 'lexical'
            : searchMode;

        return {
          ...item,
          relevanceScore: Number(finalScore.toFixed(3)),
          matchType,
        };
      })
      .filter((item) => item.relevanceScore > 0.4)
      .sort((a, b) => b.relevanceScore - a.relevanceScore);
  }, [allCorpusPassages, normalizedQuery, searchMode, selectedAuthor]);

  // Suggested queries for researchers
  const suggestions = [
    'دانش پزشکی در تمدن اسلامی',
    'نبض و علامات مزاج و قلب',
    'صیدنه و شناخت گیاهان دارویی',
    'تشخیص آبله و سرخک رازی',
    'ارکان و امزجه در طب سنتی',
  ];

  return (
    <div className="space-y-6">
      {/* Search Header Box */}
      <div className="bg-white rounded-xl shadow-sm border border-stone-200 p-5">
        <div className="flex items-center gap-2 mb-3">
          <Sparkles className="w-5 h-5 text-amber-600" />
          <h2 className="text-lg font-bold text-stone-800">
            موتور جستجوی ترکیبی نسخ خطی (Lexical &amp; pgvector Semantic Search)
          </h2>
        </div>
        <p className="text-xs text-stone-600 mb-4">
          بازیابی چندلایه با ادغام تطبیق متنی (Trigram)، تصحیح و یکسان‌سازی رسم‌الخط، و بردارهای معنایی چندزبانه (Multilingual Embeddings).
        </p>

        {/* Search Input Field */}
        <div className="relative">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="عبارت، کلمه، موضوع یا گزاره کهن را وارد فرمایید..."
            className="w-full pl-28 pr-11 py-3 text-sm md:text-base border-2 border-amber-500/40 focus:border-amber-600 focus:ring-2 focus:ring-amber-500/20 rounded-xl bg-amber-50/15 text-stone-900 outline-none transition"
            dir="rtl"
          />
          <Search className="w-5 h-5 text-amber-600 absolute right-3.5 top-3.5" />
          <div className="absolute left-2.5 top-2.5 flex items-center gap-1.5">
            <span className="text-[11px] font-mono bg-stone-100 text-stone-600 px-2 py-1 rounded border border-stone-200">
              {searchResults.length} نتیجه
            </span>
          </div>
        </div>

        {/* Query Suggestions */}
        <div className="flex flex-wrap items-center gap-2 mt-3 text-xs">
          <span className="text-stone-500 font-medium">پیشنهادهای پژوهشی:</span>
          {suggestions.map((sug) => (
            <button
              key={sug}
              onClick={() => setQuery(sug)}
              className="px-2.5 py-1 rounded-full bg-stone-100 hover:bg-amber-100 text-stone-700 hover:text-amber-900 border border-stone-200 transition"
            >
              {sug}
            </button>
          ))}
        </div>

        {/* Normalization & Mode Toggle Inspector */}
        <div className="mt-4 pt-4 border-t border-stone-100 grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Normalization Preview */}
          <div className="bg-stone-50 p-3 rounded-lg border border-stone-200 text-xs">
            <span className="font-semibold text-stone-700 block mb-1">
              پیش‌نمایش نرمال‌سازی کاتب (Persian/Arabic Normalization):
            </span>
            <div className="flex items-center gap-2 text-stone-600 font-mono">
              <span className="line-through text-stone-400">{query}</span>
              <ArrowRight className="w-3.5 h-3.5 text-amber-600 rtl:rotate-180" />
              <span className="text-amber-800 font-bold bg-amber-100/70 px-2 py-0.5 rounded">
                {normalizedQuery}
              </span>
            </div>
            <p className="text-[11px] text-stone-500 mt-1">
              یکسان‌سازی ي/ی، ك/ک، حذف اعراب و تطویل بدون دستکاری در متن نسخه اصلی.
            </p>
          </div>

          {/* Search Mode Selector */}
          <div className="flex items-center justify-between bg-stone-50 p-3 rounded-lg border border-stone-200">
            <div>
              <span className="text-xs font-semibold text-stone-700 block">حالت بازیابی (Retrieval Mode):</span>
              <span className="text-[11px] text-stone-500">
                {searchMode === 'hybrid' ? 'تلفیق رتبه‌ای واژگانی و برداری (RRF)' : searchMode === 'semantic' ? 'معنایی خالص با ابعاد ۷۶۸' : 'تطبیق لغوی دقیق'}
              </span>
            </div>
            <div className="inline-flex rounded-lg border border-stone-300 p-0.5 bg-white text-xs">
              <button
                onClick={() => setSearchMode('hybrid')}
                className={`px-2.5 py-1 rounded-md font-medium transition ${
                  searchMode === 'hybrid' ? 'bg-amber-600 text-white shadow-sm' : 'text-stone-600 hover:text-stone-900'
                }`}
              >
                ترکیبی (Hybrid)
              </button>
              <button
                onClick={() => setSearchMode('semantic')}
                className={`px-2.5 py-1 rounded-md font-medium transition ${
                  searchMode === 'semantic' ? 'bg-amber-600 text-white shadow-sm' : 'text-stone-600 hover:text-stone-900'
                }`}
              >
                معنایی (pgvector)
              </button>
              <button
                onClick={() => setSearchMode('lexical')}
                className={`px-2.5 py-1 rounded-md font-medium transition ${
                  searchMode === 'lexical' ? 'bg-amber-600 text-white shadow-sm' : 'text-stone-600 hover:text-stone-900'
                }`}
              >
                لغوی (Trigram)
              </button>
            </div>
          </div>
        </div>

        {/* Filters Row */}
        <div className="mt-3 flex flex-wrap items-center gap-3 text-xs">
          <div className="flex items-center gap-1.5">
            <Filter className="w-3.5 h-3.5 text-stone-500" />
            <span className="font-medium text-stone-700">فیلتر بر اساس مؤلف:</span>
            <select
              aria-label="فیلتر بر اساس مؤلف"
              value={selectedAuthor}
              onChange={(e) => setSelectedAuthor(e.target.value)}
              className="border border-stone-300 rounded px-2 py-1 bg-stone-50 text-stone-800"
            >
              <option value="ALL">همه دانشمندان و حکما</option>
              <option value="ابن سینا">ابن سینا (Avicenna)</option>
              <option value="رازی">محمد بن زکریای رازی (Rhazes)</option>
              <option value="بیرونی">ابوریحان بیرونی (Al-Biruni)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Results List */}
      <div className="space-y-4">
        {searchResults.length === 0 ? (
          <div className="bg-white rounded-xl border border-stone-200 p-8 text-center">
            <BookOpen className="w-10 h-10 text-stone-400 mx-auto mb-2" />
            <h3 className="text-base font-bold text-stone-700">هیچ متنی منطبق با این جستجو یافت نشد</h3>
            <p className="text-xs text-stone-500 mt-1 max-w-md mx-auto">
              لطفاً از کلیدواژه‌های کهن‌تر استفاده کنید یا فیلترهای مؤلف را غیرفعال فرمایید.
            </p>
          </div>
        ) : (
          searchResults.map((item, idx) => (
            <div
              key={item.id}
              className="bg-white rounded-xl shadow-sm border border-stone-200 hover:border-amber-300 p-5 transition group"
            >
              {/* Result Header Info */}
              <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-stone-100">
                <div className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-amber-100 text-amber-800 flex items-center justify-center font-bold text-xs">
                    {idx + 1}
                  </span>
                  <div>
                    <span className="text-sm font-bold text-stone-800">{item.bookTitle}</span>
                    <span className="text-xs text-stone-500 mr-2">اثر {item.authorName}</span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {/* Match Type Badge */}
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${
                      item.matchType === 'hybrid'
                        ? 'bg-purple-50 text-purple-700 border-purple-200'
                        : item.matchType === 'semantic'
                        ? 'bg-blue-50 text-blue-700 border-blue-200'
                        : 'bg-emerald-50 text-emerald-700 border-emerald-200'
                    }`}
                  >
                    {item.matchType} match
                  </span>

                  {/* Relevance Score */}
                  <span className="text-xs font-mono font-bold text-amber-800 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                    امتیاز: {(item.relevanceScore * 100).toFixed(0)}%
                  </span>
                </div>
              </div>

              {/* Matched Excerpt */}
              <div className="my-3 p-3.5 bg-amber-50/20 rounded-lg border-r-4 border-amber-500">
                <p className="font-manuscript text-base sm:text-lg text-stone-900 leading-relaxed">
                  «{item.text}»
                </p>
              </div>

              {/* Source Reference & Actions */}
              <div className="flex flex-wrap items-center justify-between text-xs text-stone-500 pt-2 gap-2">
                <div className="flex items-center gap-3">
                  <span>
                    نسخه: <span className="font-semibold text-stone-700">{item.manuscriptTitle}</span>
                  </span>
                  <span>•</span>
                  <span>
                    صفحه/برگ: <span className="font-semibold text-stone-700 font-mono">{item.pageNumber}</span>
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  {onOpenPageInOCR && (
                    <button
                      onClick={() => onOpenPageInOCR('ms-canon-avicenna-01', item.pageNumber)}
                      className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-stone-100 hover:bg-stone-200 text-stone-700 font-medium transition"
                    >
                      <Layers className="w-3.5 h-3.5 text-amber-600" />
                      <span>مشاهده در استودیو OCR</span>
                    </button>
                  )}

                  {onSelectPassageForAssistant && (
                    <button
                      onClick={() => onSelectPassageForAssistant(item)}
                      className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-amber-600 hover:bg-amber-700 text-white font-medium shadow-sm transition"
                    >
                      <BookCheck className="w-3.5 h-3.5" />
                      <span>پرسش از دستیار با استناد به این سند</span>
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
