import React, { useState } from 'react';
import {
  Database,
  Calculator,
  Download,
  ShieldCheck,
  FileSpreadsheet,
  Cpu,
  BarChart2,
  CheckCircle2,
  ArrowRight,
} from 'lucide-react';
import { calculateCER, calculateWER } from '../utils/pure_logic';

export const DatasetStudio: React.FC = () => {
  // Interactive CER/WER benchmark playground
  const [referenceText, setReferenceText] = useState('الطب علم يتعرف منه احوال بدن الانسان من جهة ما يصح وما يزول عن الصحة');
  const [hypothesisText, setHypothesisText] = useState('الطب علم يتعرف منه احوال بدن الانسان من جهه ما یصح وما یزول عن الصحه');

  const cer = calculateCER(referenceText, hypothesisText);
  const wer = calculateWER(referenceText, hypothesisText);

  // Mocked dataset metadata
  const datasetStats = {
    name: 'Makhtootat-Paleography-Corpus',
    version: '2.1.0',
    totalSamples: 1450,
    train: 1015,
    val: 217,
    test: 218,
    scripts: [
      { name: 'Naskh (نسخ)', count: 820, cer: '5.4%' },
      { name: 'Nastaliq (نستعلیق)', count: 410, cer: '8.2%' },
      { name: 'Thuluth & Ruqah (ثلث و رقعه)', count: 220, cer: '11.6%' },
    ],
  };

  const handleDownloadJSONL = () => {
    const sampleExport = [
      {
        id: 'sample-001',
        manuscript_id: 'ms-canon-avicenna-01',
        image_path: 'uploads/samples/canon_folio_1.jpg',
        ground_truth: referenceText,
        split: 'train',
        script: 'Naskh',
      },
      {
        id: 'sample-002',
        manuscript_id: 'ms-canon-avicenna-01',
        image_path: 'uploads/samples/canon_folio_14.jpg',
        ground_truth: 'النبض حركة في القلب والشرايين تعرض على شكل انبساط وانقباض',
        split: 'train',
        script: 'Naskh',
      },
    ];

    const blob = new Blob([sampleExport.map((x) => JSON.stringify(x)).join('\n')], {
      type: 'application/jsonl',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'makhtootat_dataset_export.jsonl';
    a.click();
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-white rounded-xl shadow-sm border border-stone-200 p-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300">
                HTR Dataset &amp; Benchmarks
              </span>
              <span className="text-xs text-stone-500 font-mono">v{datasetStats.version}</span>
            </div>
            <h2 className="text-lg font-bold text-stone-800 mt-1">
              مدیریت دادگان، ارزیابی خطا (CER/WER) و آموزش مدل TrOCR
            </h2>
            <p className="text-xs text-stone-600">
              مدیریت نمونه‌های برچسب‌دار، تفکیک بدون نشت (Zero Data Leakage)، و استخراج داده با فرمت استاندارد JSONL.
            </p>
          </div>

          <button
            onClick={handleDownloadJSONL}
            className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold shadow-sm transition"
          >
            <Download className="w-4 h-4" />
            <span>خروجی استاندارد JSONL</span>
          </button>
        </div>

        {/* Dataset Splits Breakdown */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-5 pt-4 border-t border-stone-100">
          <div className="p-3 bg-stone-50 rounded-lg border border-stone-200">
            <span className="text-[11px] text-stone-500 block">کل نمونه‌های سطربندی:</span>
            <span className="text-lg font-bold text-stone-800 font-mono">{datasetStats.totalSamples}</span>
          </div>
          <div className="p-3 bg-stone-50 rounded-lg border border-stone-200">
            <span className="text-[11px] text-stone-500 block">مجموعه آموزش (Train - 70%):</span>
            <span className="text-lg font-bold text-emerald-700 font-mono">{datasetStats.train}</span>
          </div>
          <div className="p-3 bg-stone-50 rounded-lg border border-stone-200">
            <span className="text-[11px] text-stone-500 block">مجموعه اعتبارسنجی (Val - 15%):</span>
            <span className="text-lg font-bold text-amber-700 font-mono">{datasetStats.val}</span>
          </div>
          <div className="p-3 bg-stone-50 rounded-lg border border-stone-200">
            <span className="text-[11px] text-stone-500 block">مجموعه آزمون (Test - 15%):</span>
            <span className="text-lg font-bold text-blue-700 font-mono">{datasetStats.test}</span>
          </div>
        </div>
      </div>

      {/* Grid: Interactive CER/WER Calculator + Training Pipeline Info */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Interactive CER/WER Metric Calculator */}
        <div className="lg:col-span-7 bg-white rounded-xl shadow-sm border border-stone-200 p-5 space-y-4">
          <div className="flex items-center gap-2 pb-2 border-b border-stone-100">
            <Calculator className="w-5 h-5 text-amber-600" />
            <div>
              <h3 className="text-sm font-bold text-stone-800">
                محاسبه‌گر برخط نرخ خطای نویسه (CER) و کلمه (WER)
              </h3>
              <p className="text-[11px] text-stone-500">
                مبتنی بر فاصله لون‌اشتاین (Levenshtein Distance) با اعمال نرمال‌سازی حروف کاتب
              </p>
            </div>
          </div>

          <div className="space-y-3">
            <div>
              <label className="text-xs font-semibold text-stone-700 block mb-1">
                متن مرجع مصحح (Ground Truth Reference):
              </label>
              <textarea
                aria-label="متن مرجع مصحح نسخه خطی"
                value={referenceText}
                onChange={(e) => setReferenceText(e.target.value)}
                rows={3}
                dir="rtl"
                className="w-full p-2.5 text-sm font-manuscript border border-stone-300 rounded-lg bg-stone-50 text-stone-800 resize-none outline-none focus:ring-2 focus:ring-amber-500"
              />
            </div>

            <div>
              <label className="text-xs font-semibold text-stone-700 block mb-1">
                خروجی مدل بازشناسی (Model Hypothesis):
              </label>
              <textarea
                aria-label="خروجی مدل بازشناسی هوش مصنوعی"
                value={hypothesisText}
                onChange={(e) => setHypothesisText(e.target.value)}
                rows={3}
                dir="rtl"
                className="w-full p-2.5 text-sm font-manuscript border border-stone-300 rounded-lg bg-stone-50 text-stone-800 resize-none outline-none focus:ring-2 focus:ring-amber-500"
              />
            </div>
          </div>

          {/* Metric Results Display */}
          <div className="grid grid-cols-2 gap-3 pt-2">
            <div className="p-3.5 rounded-lg bg-amber-50 border border-amber-200">
              <span className="text-xs font-bold text-stone-700 block">
                نرخ خطای نویسه (CER):
              </span>
              <span className="text-2xl font-bold font-mono text-amber-900 mt-1 block">
                {(cer * 100).toFixed(2)}%
              </span>
              <span className="text-[11px] text-stone-500 mt-0.5 block">
                {cer === 0 ? 'تطبیق ۱۰۰٪ بدون خطا' : cer < 0.1 ? 'دقت عالی مناسب نشر دانشگاهی' : 'نیازمند بازبینی کاتب'}
              </span>
            </div>

            <div className="p-3.5 rounded-lg bg-stone-100 border border-stone-200">
              <span className="text-xs font-bold text-stone-700 block">
                نرخ خطای کلمه (WER):
              </span>
              <span className="text-2xl font-bold font-mono text-stone-900 mt-1 block">
                {(wer * 100).toFixed(2)}%
              </span>
              <span className="text-[11px] text-stone-500 mt-0.5 block">
                نسبت واژگان حذف‌شده، افزوده یا تغییریافته
              </span>
            </div>
          </div>
        </div>

        {/* Training Pipeline Specifications */}
        <div className="lg:col-span-5 bg-white rounded-xl shadow-sm border border-stone-200 p-5 space-y-4">
          <div className="flex items-center gap-2 pb-2 border-b border-stone-100">
            <Cpu className="w-5 h-5 text-indigo-600" />
            <h3 className="text-sm font-bold text-stone-800">
              دستورالعمل آموزش مدل TrOCR (PyTorch)
            </h3>
          </div>

          <div className="text-xs text-stone-600 space-y-2 leading-relaxed">
            <p>
              آموزش مدل‌های HTR با حفظ تفکیک کامل نسخه‌ها انجام می‌پذیرد تا هیچ دو برگه از یک نسخه در دسته‌های آموزش و آزمون به صورت مشترک قرار نگیرند (Zero Leakage).
            </p>

            <div dir="ltr" className="p-3 rounded-lg bg-stone-900 text-stone-200 font-mono text-[11px] overflow-x-auto text-left">
              # فرمان آموزش با اسکریپت بک‌اند:<br />
              python scripts/train_htr.py \<br />
              &nbsp;&nbsp;--dataset_path ./data/dataset.jsonl \<br />
              &nbsp;&nbsp;--epochs 15 --batch_size 8 \<br />
              &nbsp;&nbsp;--learning_rate 5e-5
            </div>
          </div>

          <div className="pt-2">
            <span className="text-xs font-bold text-stone-700 block mb-2">
              نتایج ارزیابی سبک‌های خوشنویسی (Benchmark by Script):
            </span>
            <div className="space-y-2">
              {datasetStats.scripts.map((s) => (
                <div key={s.name} className="flex items-center justify-between p-2 rounded-lg bg-stone-50 border border-stone-200 text-xs">
                  <span className="font-semibold text-stone-800">{s.name}</span>
                  <div className="flex items-center gap-3">
                    <span className="text-stone-500">{s.count} نمونه</span>
                    <span className="font-mono font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                      CER: {s.cer}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
