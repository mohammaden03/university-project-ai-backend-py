import React, { useState } from 'react';
import {
  Terminal,
  Database,
  Layers,
  Server,
  FileCode,
  Shield,
  Cpu,
  ChevronRight,
  Code2,
} from 'lucide-react';

export const BackendArchitectureViewer: React.FC = () => {
  const [selectedEndpoint, setSelectedEndpoint] = useState<string>('search');

  const endpoints = [
    {
      id: 'search',
      method: 'POST',
      path: '/api/v1/search',
      desc: 'جستجوی ترکیبی واژگانی (Trigram) و معنایی (pgvector) با رتبه‌بندی RRF',
      sampleRequest: `{
  "query": "دانش پزشکی در تمدن اسلامی",
  "mode": "hybrid",
  "filters": {
    "book_id": null,
    "author_id": null
  },
  "page": 1,
  "page_size": 10
}`,
      sampleResponse: `{
  "query": "دانش پزشکی در تمدن اسلامی",
  "normalized_query": "دانش پزشکی در تمدن اسلامی",
  "total": 25,
  "results": [
    {
      "id": "transcription-uuid",
      "text": "الطب علم يتعرف منه احوال بدن الانسان...",
      "book": { "title": "قانون فی الطب" },
      "author": { "name": "ابن سینا" },
      "page_number": 1,
      "relevance_score": 0.94,
      "match_type": "hybrid"
    }
  ]
}`,
    },
    {
      id: 'ocr',
      method: 'POST',
      path: '/api/v1/ocr/recognize',
      desc: 'بازشناسی متن کهن از تصویر برگه با پیش‌پردازش، سطربندی و محاسبه اطمینان لاجیت',
      sampleRequest: `{
  "file_path": "uploads/samples/canon_folio_1.jpg",
  "model_name": "trocr_handwritten_persian",
  "enhance_contrast": true,
  "deskew": true,
  "async_processing": false
}`,
      sampleResponse: `{
  "job_id": "c1f7b8a2-...",
  "status": "COMPLETED",
  "text": "بسم الله الرحمن الرحیم قال الشیخ الرئیس...",
  "confidence": 0.94,
  "lines": [
    {
      "line_index": 1,
      "text": "بسم الله الرحمن الرحیم وبه ثقتی",
      "confidence": 0.98,
      "bounding_box": { "x": 15, "y": 12, "width": 70, "height": 8 }
    }
  ],
  "warnings": []
}`,
    },
    {
      id: 'chat_stream',
      method: 'POST',
      path: '/api/v1/chat/conversations/{id}/messages/stream',
      desc: 'استریمینگ SSE دستیار پژوهشی RAG با ارسال توکن‌ها و کارت‌های استناد [SRC-X]',
      sampleRequest: `{
  "content": "شیخ الرئیس ابن سینا طب را چگونه تعریف فرموده است؟"
}`,
      sampleResponse: `event: message_start
data: {"query": "شیخ الرئیس..."}

event: source
data: {"source_id": "SRC-1", "book_title": "قانون فی الطب", "page_number": 1}

event: token
data: {"token": "بر اساس نسخه خطی کهن قانون فی الطب [SRC-1]..."}

event: message_complete
data: {"status": "success"}`,
    },
    {
      id: 'transcriptions',
      method: 'PUT',
      path: '/api/v1/transcriptions/{id}',
      desc: 'ثبت تصحیح مصحح بدون بازنویسی یا حذف خروجی خام اولیه OCR',
      sampleRequest: `{
  "corrected_text": "متن تصحیح شده مصحح بدون حذف رکورد اولیه OCR"
}`,
      sampleResponse: `{
  "id": "transcription-uuid",
  "original_recognized_text": "متن اولیه OCR...",
  "corrected_text": "متن تصحیح شده...",
  "verification_status": "VERIFIED"
}`,
    },
  ];

  const activeEp = endpoints.find((e) => e.id === selectedEndpoint) || endpoints[0];

  return (
    <div className="space-y-6">
      {/* Overview Banner */}
      <div className="bg-stone-900 text-stone-100 rounded-xl p-5 border border-amber-900/50 shadow-md">
        <div className="flex items-center gap-2 mb-2">
          <Server className="w-5 h-5 text-amber-400" />
          <h2 className="text-lg font-bold text-amber-200">
            معماری جامع بک‌اند پایتون (Python 3.12, FastAPI, PostgreSQL &amp; pgvector)
          </h2>
        </div>
        <p className="text-xs text-stone-300 leading-relaxed max-w-4xl">
          طراحی مبتنی بر معماری تمیز (Clean Architecture) با تفکیک کامل لایه‌های Core، API v1، Models، Schemas، Services، Repositories، Storage Drivers و کارگران ناهمگام Celery.
        </p>

        {/* Stack Badges */}
        <div className="flex flex-wrap items-center gap-2 mt-4 pt-3 border-t border-stone-800">
          <span className="px-2.5 py-1 rounded bg-stone-800 text-stone-300 border border-stone-700 text-xs font-mono">
            FastAPI 0.110+
          </span>
          <span className="px-2.5 py-1 rounded bg-stone-800 text-stone-300 border border-stone-700 text-xs font-mono">
            SQLAlchemy 2.0 Async
          </span>
          <span className="px-2.5 py-1 rounded bg-stone-800 text-stone-300 border border-stone-700 text-xs font-mono">
            PostgreSQL 16 + pgvector
          </span>
          <span className="px-2.5 py-1 rounded bg-stone-800 text-stone-300 border border-stone-700 text-xs font-mono">
            Celery 5.3 + Redis 7
          </span>
          <span className="px-2.5 py-1 rounded bg-stone-800 text-stone-300 border border-stone-700 text-xs font-mono">
            PyTorch + TrOCR Adapter
          </span>
          <span className="px-2.5 py-1 rounded bg-stone-800 text-stone-300 border border-stone-700 text-xs font-mono">
            Alembic Migrations
          </span>
        </div>
      </div>

      {/* Grid: Endpoints Explorer + ERD Architecture */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Endpoints Sidebar */}
        <div className="lg:col-span-4 bg-white rounded-xl shadow-sm border border-stone-200 p-4 space-y-3">
          <h3 className="text-xs font-bold text-stone-700 flex items-center gap-1.5 pb-2 border-b border-stone-100">
            <Terminal className="w-4 h-4 text-amber-600" />
            <span>فهرست نقاط پایانی RESTful API (v1):</span>
          </h3>

          <div className="space-y-1.5">
            {endpoints.map((ep) => {
              const isSelected = selectedEndpoint === ep.id;
              return (
                <div
                  key={ep.id}
                  onClick={() => setSelectedEndpoint(ep.id)}
                  className={`p-2.5 rounded-lg border text-xs cursor-pointer transition ${
                    isSelected
                      ? 'bg-amber-50 border-amber-400 text-stone-900 shadow-sm'
                      : 'bg-stone-50 border-stone-200 hover:bg-stone-100/70 text-stone-700'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span
                      className={`font-mono text-[10px] px-1.5 py-0.2 rounded font-bold ${
                        ep.method === 'POST'
                          ? 'bg-emerald-100 text-emerald-800'
                          : 'bg-blue-100 text-blue-800'
                      }`}
                    >
                      {ep.method}
                    </span>
                    <span className="font-mono text-[11px] text-stone-600">{ep.path}</span>
                  </div>
                  <p className="text-[11px] text-stone-500 line-clamp-1">{ep.desc}</p>
                </div>
              );
            })}
          </div>

          <div className="pt-3 border-t border-stone-100 text-[11px] text-stone-500 space-y-1">
            <p>مستندات کامل Swagger UI در دسترس در مسیر:</p>
            <code className="text-amber-800 font-mono bg-amber-50 px-2 py-0.5 rounded block text-center">
              GET /docs &amp; GET /redoc
            </code>
          </div>
        </div>

        {/* Selected Endpoint Request & Response Inspector */}
        <div className="lg:col-span-8 bg-white rounded-xl shadow-sm border border-stone-200 p-5 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-stone-100">
            <div className="flex items-center gap-2">
              <span
                className={`font-mono text-xs px-2.5 py-0.5 rounded font-bold ${
                  activeEp.method === 'POST'
                    ? 'bg-emerald-100 text-emerald-800'
                    : 'bg-blue-100 text-blue-800'
                }`}
              >
                {activeEp.method}
              </span>
              <span className="font-mono text-sm font-bold text-stone-800">{activeEp.path}</span>
            </div>
            <span className="text-xs text-stone-500">FastAPI Router V1</span>
          </div>

          <p className="text-xs text-stone-700 bg-stone-50 p-2.5 rounded-lg border border-stone-200">
            {activeEp.desc}
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Request Body */}
            <div>
              <span className="text-xs font-bold text-stone-700 block mb-1.5 flex items-center gap-1">
                <Code2 className="w-3.5 h-3.5 text-stone-500" />
                <span>نمونه بدنه درخواست (Request JSON):</span>
              </span>
              <pre dir="ltr" className="p-3 rounded-lg bg-stone-900 text-amber-200 font-mono text-[11px] overflow-x-auto h-64 border border-stone-800 text-left">
                {activeEp.sampleRequest}
              </pre>
            </div>

            {/* Response Body */}
            <div>
              <span className="text-xs font-bold text-stone-700 block mb-1.5 flex items-center gap-1">
                <Code2 className="w-3.5 h-3.5 text-emerald-600" />
                <span>نمونه پاسخ سرور (Response 200 OK):</span>
              </span>
              <pre dir="ltr" className="p-3 rounded-lg bg-stone-900 text-emerald-300 font-mono text-[11px] overflow-x-auto h-64 border border-stone-800 text-left">
                {activeEp.sampleResponse}
              </pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
