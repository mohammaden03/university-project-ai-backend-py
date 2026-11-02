import React, { useState } from 'react';
import { Header, ActiveTab } from './components/Header';
import { OCRStudio } from './components/OCRStudio';
import { HybridSearch } from './components/HybridSearch';
import { ResearchAssistant } from './components/ResearchAssistant';
import { ManuscriptCatalog } from './components/ManuscriptCatalog';
import { DatasetStudio } from './components/DatasetStudio';
import { BackendArchitectureViewer } from './components/BackendArchitectureViewer';
import { SearchResultItem } from './utils/pure_logic';

export default function App() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('ocr');
  const [lang, setLang] = useState<'fa' | 'en'>('fa');

  // Callback to transition from search to assistant
  const handleSelectPassageForAssistant = (passage: SearchResultItem) => {
    setActiveTab('chat');
  };

  // Callback to transition from catalog/search to OCR
  const handleOpenPageInOCR = (manuscriptId: string, pageNumber: number) => {
    setActiveTab('ocr');
  };

  return (
    <div className="min-h-screen bg-stone-100 flex flex-col font-sans" dir={lang === 'fa' ? 'rtl' : 'ltr'}>
      {/* Navigation Header */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        lang={lang}
        setLang={setLang}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === 'ocr' && <OCRStudio />}
        {activeTab === 'search' && (
          <HybridSearch
            onSelectPassageForAssistant={handleSelectPassageForAssistant}
            onOpenPageInOCR={handleOpenPageInOCR}
          />
        )}
        {activeTab === 'chat' && <ResearchAssistant />}
        {activeTab === 'catalog' && (
          <ManuscriptCatalog onSelectManuscriptForOCR={() => setActiveTab('ocr')} />
        )}
        {activeTab === 'dataset' && <DatasetStudio />}
        {activeTab === 'architecture' && <BackendArchitectureViewer />}
      </main>

      {/* Footer */}
      <footer className="bg-stone-900 border-t border-amber-900/40 text-stone-400 py-6 text-xs text-center">
        <div className="max-w-7xl mx-auto px-4 space-y-1">
          <p className="text-stone-300 font-medium">
            پروژه تحقیقاتی هوش مصنوعی مخطوطات • سامانه ملی شناسایی و جستجوی نسخ خطی کهن
          </p>
          <p className="text-stone-500 font-mono text-[11px]">
            Makhtootat Platform • FastAPI • PostgreSQL 16 pgvector • Celery &amp; Redis • TrOCR Multilingual
          </p>
        </div>
      </footer>
    </div>
  );
}
