import React from 'react';
import {
  BookOpen,
  ScanText,
  Search,
  MessageSquareQuote,
  Database,
  Layers,
  Terminal,
  Globe,
  CheckCircle2,
} from 'lucide-react';

export type ActiveTab = 'ocr' | 'search' | 'chat' | 'catalog' | 'dataset' | 'architecture';

interface HeaderProps {
  activeTab: ActiveTab;
  setActiveTab: (tab: ActiveTab) => void;
  lang: 'fa' | 'en';
  setLang: (lang: 'fa' | 'en') => void;
}

export const Header: React.FC<HeaderProps> = ({ activeTab, setActiveTab, lang, setLang }) => {
  const isFa = lang === 'fa';

  const navItems = [
    { id: 'ocr' as ActiveTab, labelFa: 'استودیو HTR/OCR', labelEn: 'HTR/OCR Studio', icon: ScanText },
    { id: 'search' as ActiveTab, labelFa: 'جستجوی ترکیبی', labelEn: 'Hybrid Search', icon: Search },
    { id: 'chat' as ActiveTab, labelFa: 'دستیار پژوهش RAG', labelEn: 'Research Assistant', icon: MessageSquareQuote },
    { id: 'catalog' as ActiveTab, labelFa: 'فهرست نسخ خطی', labelEn: 'Manuscripts Catalog', icon: BookOpen },
    { id: 'dataset' as ActiveTab, labelFa: 'مدیریت دیتاست و CER', labelEn: 'Datasets & CER', icon: Database },
    { id: 'architecture' as ActiveTab, labelFa: 'معماری بک‌اند و API', labelEn: 'Backend & API', icon: Terminal },
  ];

  return (
    <header className="bg-stone-900 border-b border-amber-900/40 text-stone-100 shadow-lg sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand */}
          <div className="flex items-center space-x-3 rtl:space-x-reverse cursor-pointer" onClick={() => setActiveTab('ocr')}>
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-amber-600 to-amber-900 flex items-center justify-center shadow-md border border-amber-500/30">
              <span className="font-manuscript text-2xl font-bold text-amber-100">خط</span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-title text-xl font-bold tracking-wide text-amber-200">
                  {isFa ? 'سامانه هوشمند مخطوطات' : 'MAKHTOOTAT'}
                </span>
                <span className="text-[10px] bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded border border-amber-500/30 font-mono">
                  v1.0 • FastAPI &amp; TrOCR
                </span>
              </div>
              <p className="text-xs text-stone-400">
                {isFa
                  ? 'شناسایی خطوط کهن، جستجوی معنایی و دستیار مستند نسخ خطی اسلامی'
                  : 'Historical Persian & Arabic Manuscript HTR, Hybrid Search & RAG'}
              </p>
            </div>
          </div>

          {/* User Badge & Language Toggle */}
          <div className="flex items-center space-x-3 rtl:space-x-reverse">
            <button
              onClick={() => setLang(isFa ? 'en' : 'fa')}
              className="flex items-center gap-1.5 px-2.5 py-1 text-xs rounded-md bg-stone-800 hover:bg-stone-700 text-stone-300 border border-stone-700 transition"
              title="تغییر زبان / Switch Language"
              aria-label="تغییر زبان"
            >
              <Globe className="w-3.5 h-3.5 text-amber-400" />
              <span>{isFa ? 'English' : 'فارسی'}</span>
            </button>

            <div className="hidden sm:flex items-center gap-2 bg-stone-800/80 px-3 py-1 rounded-full border border-stone-700 text-xs text-stone-300">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-stone-300 font-medium">دکتر انتصاری (پژوهشگر ارشد)</span>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex space-x-1 rtl:space-x-reverse overflow-x-auto py-2 border-t border-stone-800/80">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center gap-2 px-3.5 py-2 text-xs sm:text-sm font-medium rounded-lg transition-all whitespace-nowrap ${
                  isActive
                    ? 'bg-amber-600 text-amber-50 shadow-sm'
                    : 'text-stone-300 hover:bg-stone-800 hover:text-amber-200'
                }`}
                role="tab"
                aria-selected={isActive}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-amber-100' : 'text-stone-400'}`} />
                <span>{isFa ? item.labelFa : item.labelEn}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
};
