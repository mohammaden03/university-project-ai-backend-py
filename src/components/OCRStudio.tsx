import React, { useState } from 'react';
import {
  Upload,
  Sliders,
  CheckCircle2,
  AlertTriangle,
  FileCheck,
  RefreshCw,
  Sparkles,
  Download,
  Eye,
  Layers,
  Info,
  Save,
  Check,
} from 'lucide-react';
import { MANUSCRIPT_COLLECTION, ManuscriptPageData } from '../data/manuscripts_data';
import { normalizePersianArabicText } from '../utils/pure_logic';

export const OCRStudio: React.FC = () => {
  // Select initial page from collection (Ibn Sina's Canon page 1)
  const [selectedManuscript, setSelectedManuscript] = useState(MANUSCRIPT_COLLECTION[0]);
  const [currentPage, setCurrentPage] = useState<ManuscriptPageData>(MANUSCRIPT_COLLECTION[0].pages[0]);

  // Preprocessing toggles
  const [claheContrast, setClaheContrast] = useState(true);
  const [deskew, setDeskew] = useState(true);
  const [denoise, setDenoise] = useState(true);
  const [showBoxes, setShowBoxes] = useState(true);

  // Model & State
  const [selectedModel, setSelectedModel] = useState('trocr_handwritten_persian');
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeLineIndex, setActiveLineIndex] = useState<number | null>(null);

  // Editable transcription state
  const [editedText, setEditedText] = useState(
    currentPage.correctedText || currentPage.originalText
  );
  const [verificationStatus, setVerificationStatus] = useState<'PENDING' | 'VERIFIED' | 'NEEDS_REVIEW'>(
    currentPage.verificationStatus
  );
  const [savedSuccessMsg, setSavedSuccessMsg] = useState('');

  // Handle switching page
  const handleSelectPage = (page: ManuscriptPageData) => {
    setCurrentPage(page);
    setEditedText(page.correctedText || page.originalText);
    setVerificationStatus(page.verificationStatus);
    setActiveLineIndex(null);
    setSavedSuccessMsg('');
  };

  // Run recognition simulation
  const handleRunRecognition = () => {
    setIsProcessing(true);
    setSavedSuccessMsg('');
    setTimeout(() => {
      setIsProcessing(false);
    }, 600);
  };

  // Save correction
  const handleSaveCorrection = () => {
    // Keep originalText unchanged; save to correctedText
    currentPage.correctedText = editedText;
    currentPage.normalizedText = normalizePersianArabicText(editedText);
    currentPage.verificationStatus = verificationStatus;
    setSavedSuccessMsg('تصحیح با موفقیت در پایگاه داده ثبت شد (متن اولیه OCR بدون تغییر حفظ گردید).');
    setTimeout(() => setSavedSuccessMsg(''), 4000);
  };

  // Custom upload handler
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const url = URL.createObjectURL(file);
      const newPage: ManuscriptPageData = {
        id: `custom-page-${Date.now()}`,
        manuscriptId: selectedManuscript.id,
        pageNumber: selectedManuscript.pages.length + 1,
        imageUrl: url,
        thumbnailUrl: url,
        originalText: 'متن بازشناسی‌شده پس از تحلیل لایه‌ای خط و استخراج حروف کهن...',
        normalizedText: 'متن بازشناسی شده پس از تحلیل لایه ای خط و استخراج حروف کهن',
        language: 'fa',
        scriptStyle: 'Naskh',
        confidenceScore: 0.88,
        verificationStatus: 'NEEDS_REVIEW',
        modelName: selectedModel,
        modelVersion: '1.0.0',
        warnings: ['تصویر بارگذاری‌شده به عنوان برگه جدید ثبت شد. تطبیق با کاتالوگ توصیه می‌گردد.'],
        lines: [
          {
            lineIndex: 1,
            text: 'سطر اول سند کهن بارگذاری شده',
            confidence: 0.9,
            box: { x: 10, y: 20, width: 80, height: 12 },
          },
          {
            lineIndex: 2,
            text: 'سطر دوم سند کهن دربردارنده اصطلاحات طبی',
            confidence: 0.86,
            box: { x: 12, y: 40, width: 76, height: 12 },
          },
        ],
      };
      selectedManuscript.pages.push(newPage);
      handleSelectPage(newPage);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner & Manuscript Selector */}
      <div className="bg-white rounded-xl shadow-sm border border-stone-200 p-4 sm:p-5">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-300">
                HTR/OCR Engine
              </span>
              <span className="text-xs text-stone-500 font-mono">
                {selectedManuscript.catalogReference}
              </span>
            </div>
            <h2 className="text-xl font-bold text-stone-800 mt-1">
              {selectedManuscript.title}
            </h2>
            <p className="text-sm text-stone-600">
              مؤلف: <span className="font-semibold text-stone-800">{selectedManuscript.authorName}</span> | رسم‌الخط: <span className="font-medium text-amber-700">{selectedManuscript.scriptStyle}</span> | {selectedManuscript.century}
            </p>
          </div>

          {/* Quick Codex Selector */}
          <div className="flex items-center gap-2">
            <label className="text-xs font-medium text-stone-700 whitespace-nowrap">انتخاب نسخه:</label>
            <select
              aria-label="انتخاب نسخه خطی"
              value={selectedManuscript.id}
              onChange={(e) => {
                const found = MANUSCRIPT_COLLECTION.find((m) => m.id === e.target.value);
                if (found) {
                  setSelectedManuscript(found);
                  handleSelectPage(found.pages[0]);
                }
              }}
              className="text-xs border border-stone-300 rounded-lg px-3 py-2 bg-stone-50 text-stone-800 focus:ring-2 focus:ring-amber-500"
            >
              {MANUSCRIPT_COLLECTION.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.bookTitle} - {m.source.split(' ')[0]}
                </option>
              ))}
            </select>

            <label className="cursor-pointer inline-flex items-center gap-1.5 px-3 py-2 bg-amber-50 hover:bg-amber-100 text-amber-800 text-xs font-medium rounded-lg border border-amber-300 transition">
              <Upload className="w-3.5 h-3.5" />
              <span>بارگذاری تصویر برگه</span>
              <input
                type="file"
                accept=".jpg,.jpeg,.png,.tiff,.tif"
                onChange={handleFileUpload}
                className="hidden"
                aria-label="بارگذاری فایل تصویر نسخه خطی"
              />
            </label>
          </div>
        </div>

        {/* Page Folios Thumbnails */}
        <div className="flex items-center gap-3 overflow-x-auto pt-4 mt-4 border-t border-stone-100">
          <span className="text-xs font-medium text-stone-500 whitespace-nowrap">برگه‌های نسخه:</span>
          {selectedManuscript.pages.map((p) => (
            <button
              key={p.id}
              onClick={() => handleSelectPage(p)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs transition whitespace-nowrap ${
                currentPage.id === p.id
                  ? 'bg-amber-600 text-white border-amber-600 font-semibold shadow-sm'
                  : 'bg-stone-50 hover:bg-stone-100 text-stone-700 border-stone-200'
              }`}
            >
              <span>برگ {p.pageNumber}</span>
              <span className={`w-2 h-2 rounded-full ${p.verificationStatus === 'VERIFIED' ? 'bg-emerald-400' : 'bg-amber-400'}`} />
            </button>
          ))}
        </div>
      </div>

      {/* Main OCR Grid: Canvas & Reviewer */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Manuscript Viewer & Preprocessing Controls */}
        <div className="lg:col-span-6 space-y-4">
          <div className="bg-white rounded-xl shadow-sm border border-stone-200 p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2 text-stone-700">
                <Sliders className="w-4 h-4 text-amber-600" />
                <h3 className="text-sm font-bold">تنظیمات پیش‌پردازش تصویر (OpenCV)</h3>
              </div>
              <div className="flex items-center gap-3 text-xs">
                <label className="inline-flex items-center gap-1.5 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={claheContrast}
                    onChange={(e) => setClaheContrast(e.target.checked)}
                    className="rounded text-amber-600 focus:ring-amber-500"
                  />
                  <span>تقویت کنتراست (CLAHE)</span>
                </label>
                <label className="inline-flex items-center gap-1.5 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={deskew}
                    onChange={(e) => setDeskew(e.target.checked)}
                    className="rounded text-amber-600 focus:ring-amber-500"
                  />
                  <span>اصلاح زاویه (Deskew)</span>
                </label>
                <label className="inline-flex items-center gap-1.5 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={showBoxes}
                    onChange={(e) => setShowBoxes(e.target.checked)}
                    className="rounded text-amber-600 focus:ring-amber-500"
                  />
                  <span>سطربندی (Boxes)</span>
                </label>
              </div>
            </div>

            {/* Manuscript Canvas Container */}
            <div className="relative border border-stone-300 rounded-lg overflow-hidden bg-stone-900 aspect-[3/4] max-h-[520px] flex items-center justify-center group shadow-inner">
              <img
                src={currentPage.imageUrl}
                alt={`Manuscript Folio ${currentPage.pageNumber}`}
                className={`w-full h-full object-contain transition-all duration-300 ${
                  claheContrast ? 'contrast-125 brightness-95' : ''
                } ${denoise ? 'blur-[0.2px]' : ''}`}
              />

              {/* Bounding Boxes Layer */}
              {showBoxes && (
                <div className="absolute inset-0 pointer-events-none">
                  {currentPage.lines.map((line) => {
                    const isHovered = activeLineIndex === line.lineIndex;
                    return (
                      <div
                        key={line.lineIndex}
                        style={{
                          left: `${line.box.x}%`,
                          top: `${line.box.y}%`,
                          width: `${line.box.width}%`,
                          height: `${line.box.height}%`,
                        }}
                        className={`absolute border rounded pointer-events-auto cursor-pointer transition-all ${
                          isHovered
                            ? 'border-emerald-400 bg-emerald-500/25 ring-2 ring-emerald-400 z-20'
                            : 'border-amber-400/80 bg-amber-500/10 hover:bg-amber-500/20 z-10'
                        }`}
                        onClick={() => setActiveLineIndex(line.lineIndex)}
                        title={`سطر ${line.lineIndex} (اطمینان: ${(line.confidence * 100).toFixed(0)}%)`}
                      >
                        <span className="absolute -top-3.5 right-1 px-1.5 py-0.2 bg-stone-900/90 text-amber-300 text-[10px] rounded font-mono border border-amber-500/40">
                          L{line.lineIndex}
                        </span>
                      </div>
                    );
                  })}
                </div>
              )}

              {/* Watermark badge */}
              <div className="absolute bottom-2 left-2 bg-stone-900/80 px-2 py-1 rounded text-[10px] text-stone-300 border border-stone-700">
                {selectedManuscript.source}
              </div>
            </div>

            <div className="flex items-center justify-between text-xs text-stone-500 mt-2 px-1">
              <span>رزولوشن اصلی: 1800×2600 پیکسل</span>
              <span>رسم‌الخط: {currentPage.scriptStyle} • راست‌به‌چپ (RTL)</span>
            </div>
          </div>
        </div>

        {/* Right Column: HTR Model, Line Inspector & Transcription Editor */}
        <div className="lg:col-span-6 space-y-4">
          {/* Recognition Engine Controls */}
          <div className="bg-white rounded-xl shadow-sm border border-stone-200 p-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-stone-100">
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold text-stone-700">مدل هوش مصنوعی:</span>
                <select
                  aria-label="انتخاب مدل هوش مصنوعی بازشناسی"
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  className="text-xs border border-stone-300 rounded-md px-2.5 py-1.5 bg-stone-50 text-stone-800"
                >
                  <option value="trocr_handwritten_persian">TrOCR Fine-Tuned (Naskh &amp; Nastaliq)</option>
                  <option value="trocr_base_handwritten">TrOCR Base (General Handwriting)</option>
                  <option value="crnn_persian_manuscript">CRNN + CTC Paleography Adapter</option>
                </select>
              </div>

              <button
                onClick={handleRunRecognition}
                disabled={isProcessing}
                className="inline-flex items-center justify-center gap-1.5 px-4 py-2 bg-amber-600 hover:bg-amber-700 disabled:bg-amber-300 text-white rounded-lg text-xs font-semibold shadow-sm transition"
              >
                {isProcessing ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>در حال بازشناسی حروف...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>اجرای بازشناسی (HTR)</span>
                  </>
                )}
              </button>
            </div>

            {/* Confidence & Warnings Section */}
            <div className="pt-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-xs text-stone-600">میزان اطمینان مدل:</span>
                <div className="flex items-center gap-1.5">
                  <div className="w-24 h-2 bg-stone-100 rounded-full overflow-hidden border border-stone-200">
                    <div
                      className={`h-full ${
                        currentPage.confidenceScore >= 0.9
                          ? 'bg-emerald-500'
                          : currentPage.confidenceScore >= 0.7
                          ? 'bg-amber-500'
                          : 'bg-rose-500'
                      }`}
                      style={{ width: `${currentPage.confidenceScore * 100}%` }}
                    />
                  </div>
                  <span className="text-xs font-mono font-bold text-stone-800">
                    {(currentPage.confidenceScore * 100).toFixed(1)}%
                  </span>
                </div>
              </div>

              {/* Status Badge */}
              <div className="flex items-center gap-1.5">
                <span className="text-xs text-stone-600">وضعیت بازبینی:</span>
                <select
                  aria-label="وضعیت بازبینی بازشناسی"
                  value={verificationStatus}
                  onChange={(e) => setVerificationStatus(e.target.value as any)}
                  className={`text-xs font-semibold px-2 py-0.5 rounded border ${
                    verificationStatus === 'VERIFIED'
                      ? 'bg-emerald-50 text-emerald-700 border-emerald-300'
                      : verificationStatus === 'NEEDS_REVIEW'
                      ? 'bg-rose-50 text-rose-700 border-rose-300'
                      : 'bg-amber-50 text-amber-700 border-amber-300'
                  }`}
                >
                  <option value="VERIFIED">تأیید شده (VERIFIED)</option>
                  <option value="PENDING">در انتظار (PENDING)</option>
                  <option value="NEEDS_REVIEW">نیازمند بازبینی (NEEDS REVIEW)</option>
                </select>
              </div>
            </div>

            {/* Paleography Warning if confidence is below 85% */}
            {currentPage.confidenceScore < 0.9 && (
              <div className="mt-3 p-2.5 rounded-lg bg-amber-50 border border-amber-200 flex items-start gap-2 text-xs text-amber-800">
                <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold">هشدار نسخه شناس و کاتب کهن:</p>
                  <p className="mt-0.5 text-stone-600">
                    در این برگ اتصال حروف و سرهم‌نویسی پیچیده (Ligatures) شناسایی شد. نتایج مدل نیازمند تطبیق چشمی توسط مصحح است.
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Line by Line Interactive List */}
          <div className="bg-white rounded-xl shadow-sm border border-stone-200 p-4">
            <h4 className="text-xs font-bold text-stone-700 mb-2.5 flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-amber-600" />
              <span>سطرهای تفکیک‌شده (جهت راست‌به‌چپ):</span>
            </h4>
            <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
              {currentPage.lines.map((line) => {
                const isActive = activeLineIndex === line.lineIndex;
                return (
                  <div
                    key={line.lineIndex}
                    onClick={() => setActiveLineIndex(line.lineIndex)}
                    className={`flex items-center justify-between p-2 rounded-lg border text-xs cursor-pointer transition ${
                      isActive
                        ? 'bg-amber-50 border-amber-400 text-stone-900 shadow-sm'
                        : 'bg-stone-50/70 border-stone-200 hover:bg-stone-100/80 text-stone-700'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-stone-200 text-stone-700">
                        سطر {line.lineIndex}
                      </span>
                      <span className="font-manuscript text-sm font-medium">{line.text}</span>
                    </div>
                    <span
                      className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${
                        line.confidence > 0.9 ? 'text-emerald-700 bg-emerald-100' : 'text-amber-700 bg-amber-100'
                      }`}
                    >
                      {(line.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Side-by-Side Full Transcription Editor */}
          <div className="bg-white rounded-xl shadow-sm border border-stone-200 p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-1.5">
                <FileCheck className="w-4 h-4 text-emerald-600" />
                <h4 className="text-sm font-bold text-stone-800">ویرایشگر و تصحیح رونویسی</h4>
              </div>
              <span className="text-[11px] text-stone-500">
                اصل بازشناسی OCR بدون تغییر ذخیره می‌ماند
              </span>
            </div>

            <textarea
              aria-label="متن بازشناسی شده نسخه خطی"
              value={editedText}
              onChange={(e) => setEditedText(e.target.value)}
              rows={6}
              dir="rtl"
              className="w-full text-base font-manuscript leading-relaxed p-3 border border-stone-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500 bg-amber-50/20 text-stone-900 resize-none"
              placeholder="متن بازشناسی شده..."
            />

            {savedSuccessMsg && (
              <div className="mt-2 p-2 rounded-lg bg-emerald-50 border border-emerald-200 flex items-center gap-2 text-xs text-emerald-800">
                <Check className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>{savedSuccessMsg}</span>
              </div>
            )}

            <div className="flex items-center justify-between mt-3 pt-2 border-t border-stone-100">
              <button
                onClick={() => setEditedText(currentPage.originalText)}
                className="text-xs text-stone-500 hover:text-stone-800 transition"
              >
                بازنشانی به متن اولیه OCR
              </button>

              <button
                onClick={handleSaveCorrection}
                className="inline-flex items-center gap-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold shadow-sm transition"
              >
                <Save className="w-3.5 h-3.5" />
                <span>ذخیره تصحیح و نمایه‌سازی (Save &amp; Index)</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
