import React, { useState } from 'react';
import { BookOpen, User, Library, FileText, Calendar, ExternalLink, Search } from 'lucide-react';
import { MANUSCRIPT_COLLECTION, ManuscriptItem } from '../data/manuscripts_data';

interface ManuscriptCatalogProps {
  onSelectManuscriptForOCR?: (manuscriptId: string) => void;
}

export const ManuscriptCatalog: React.FC<ManuscriptCatalogProps> = ({ onSelectManuscriptForOCR }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedManuscript, setSelectedManuscript] = useState<ManuscriptItem>(MANUSCRIPT_COLLECTION[0]);

  const filteredManuscripts = MANUSCRIPT_COLLECTION.filter((m) => {
    const term = searchTerm.toLowerCase();
    return (
      m.title.toLowerCase().includes(term) ||
      m.authorName.toLowerCase().includes(term) ||
      m.bookTitle.toLowerCase().includes(term) ||
      m.source.toLowerCase().includes(term)
    );
  });

  return (
    <div className="space-y-6">
      {/* Search & Filter Bar */}
      <div className="bg-white rounded-xl shadow-sm border border-stone-200 p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="relative flex-1">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="جستجو در کتب، مؤلفان، کتابخانه‌ها و سبک‌های نگارش..."
            className="w-full pl-4 pr-10 py-2.5 text-xs sm:text-sm border border-stone-300 rounded-lg bg-stone-50 text-stone-800 focus:ring-2 focus:ring-amber-500 outline-none"
            dir="rtl"
          />
          <Search className="w-4 h-4 text-stone-400 absolute right-3 top-3" />
        </div>
        <div className="text-xs text-stone-500 font-mono">
          {filteredManuscripts.length} نسخه خطی ثبت‌شده
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Manuscripts List */}
        <div className="lg:col-span-5 space-y-3">
          {filteredManuscripts.map((ms) => {
            const isSelected = selectedManuscript.id === ms.id;
            return (
              <div
                key={ms.id}
                onClick={() => setSelectedManuscript(ms)}
                className={`p-4 rounded-xl border cursor-pointer transition ${
                  isSelected
                    ? 'bg-amber-50/70 border-amber-500 shadow-sm'
                    : 'bg-white border-stone-200 hover:border-amber-300'
                }`}
              >
                <div className="flex items-center justify-between gap-2 mb-1.5">
                  <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-amber-100 text-amber-800">
                    رسم‌الخط {ms.scriptStyle}
                  </span>
                  <span className="text-[11px] text-stone-500 font-mono">{ms.century}</span>
                </div>
                <h3 className="text-sm font-bold text-stone-800">{ms.title}</h3>
                <p className="text-xs text-stone-600 mt-1">
                  کتاب: <span className="font-semibold">{ms.bookTitle}</span> | اثر: {ms.authorName}
                </p>
                <div className="flex items-center gap-1.5 text-[11px] text-stone-500 mt-2">
                  <Library className="w-3.5 h-3.5 text-stone-400" />
                  <span>{ms.source}</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Selected Manuscript Codex Detail */}
        <div className="lg:col-span-7 bg-white rounded-xl shadow-sm border border-stone-200 p-6 space-y-5">
          <div>
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono text-amber-800 bg-amber-100 px-2.5 py-0.5 rounded font-semibold">
                {selectedManuscript.catalogReference}
              </span>
              <span className="text-xs text-stone-500 font-medium">زبان: {selectedManuscript.language === 'fa' ? 'فارسی کهن' : 'عربی'}</span>
            </div>
            <h2 className="text-xl font-bold text-stone-900 mt-2">{selectedManuscript.title}</h2>
            <p className="text-sm text-stone-600 mt-1">
              کتاب: <span className="font-semibold text-stone-800">{selectedManuscript.bookTitle}</span> | اثر: <span className="font-semibold text-stone-800">{selectedManuscript.authorName}</span>
            </p>
          </div>

          <p className="text-xs sm:text-sm text-stone-700 leading-relaxed bg-stone-50 p-4 rounded-lg border border-stone-200">
            {selectedManuscript.description}
          </p>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="p-3 bg-stone-50 rounded-lg border border-stone-200">
              <span className="text-stone-500 block text-[11px]">منبع و کتابخانه:</span>
              <span className="font-semibold text-stone-800">{selectedManuscript.source}</span>
            </div>
            <div className="p-3 bg-stone-50 rounded-lg border border-stone-200">
              <span className="text-stone-500 block text-[11px]">مجموعه خطی:</span>
              <span className="font-semibold text-stone-800">{selectedManuscript.collectionName}</span>
            </div>
          </div>

          {/* Folio Gallery */}
          <div>
            <h4 className="text-xs font-bold text-stone-700 mb-3 flex items-center gap-1.5">
              <FileText className="w-4 h-4 text-amber-600" />
              <span>برگه‌های موجود در پایگاه:</span>
            </h4>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {selectedManuscript.pages.map((p) => (
                <div
                  key={p.id}
                  className="group relative rounded-lg overflow-hidden border border-stone-300 aspect-[3/4] bg-stone-900"
                >
                  <img
                    src={p.imageUrl}
                    alt={`Folio ${p.pageNumber}`}
                    className="w-full h-full object-cover group-hover:scale-105 transition duration-300"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent flex flex-col justify-end p-2.5">
                    <span className="text-xs font-bold text-amber-200">برگ {p.pageNumber}</span>
                    <span className="text-[10px] text-stone-300 font-mono">
                      اطمینان: {(p.confidenceScore * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {onSelectManuscriptForOCR && (
            <div className="pt-3 border-t border-stone-200 flex justify-end">
              <button
                onClick={() => onSelectManuscriptForOCR(selectedManuscript.id)}
                className="inline-flex items-center gap-1.5 px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white text-xs font-semibold rounded-lg shadow-sm transition"
              >
                <span>انتقال برگه‌ها به استودیو بازشناسی OCR</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
