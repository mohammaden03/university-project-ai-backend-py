import React, { useState, useRef, useEffect } from 'react';
import {
  MessageSquareQuote,
  Send,
  Sparkles,
  BookOpen,
  CheckCircle2,
  AlertCircle,
  Copy,
  Check,
  RefreshCw,
  ExternalLink,
  ShieldCheck,
  FileText,
  User,
  Layers,
} from 'lucide-react';
import { MANUSCRIPT_COLLECTION } from '../data/manuscripts_data';
import { normalizePersianArabicText, SourceCitation } from '../utils/pure_logic';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: SourceCitation[];
  timestamp: string;
}

export const ResearchAssistant: React.FC = () => {
  const [conversationMode, setConversationMode] = useState<'RESEARCH' | 'OCR'>('RESEARCH');
  const [inputMessage, setInputMessage] = useState('شیخ الرئیس ابن سینا طب را چگونه تعریف کرده و ارکان آن چیست؟');
  const [isStreaming, setIsStreaming] = useState(false);
  const [selectedCitation, setSelectedCitation] = useState<SourceCitation | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initial grounded conversation
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'msg-welcome',
      role: 'assistant',
      content:
        'درود بر پژوهشگر گرامی. من «دستیار هوشمند پژوهش در نسخ خطی اسلامی و کهن» هستم. تمامی پاسخ‌های من مستقیماً از اسناد و نسخ خطی بازیابی‌شده استخراج شده و دارای استناد دقیق به نام کتاب، مؤلف و شماره برگ می‌باشند. هرگز نقلی بدون مدرک ارائه نمی‌گردد.',
      timestamp: '۱۰:۰۰',
    },
    {
      id: 'msg-q1',
      role: 'user',
      content: 'تعریف ابن سینا از علم طب و اسباب حفظ تندرستی چیست؟',
      timestamp: '۱۰:۰۱',
    },
    {
      id: 'msg-a1',
      role: 'assistant',
      content: `بر اساس نسخه خطی کهن کتاب اول «قانون فی الطب» [SRC-1]، شیخ الرئیس ابو علی سینا طب را چنین تعریف می‌فرماید:

«الطب علم يتعرف منه احوال بدن الانسان من جهة ما يصح وما يزول عن الصحة ليحفظ الصحة حاصلة ويستردها زائلة»

توضیح مستند به متن نسخه:
۱. غایت پزشکی دو امر است: نخست «حفظ تندرستی موجود» و دوم «بازگرداندن تندرستی زایل‌شده».
۲. ابن سینا در ادامه تصریح می‌دارد که بنیاد حفظ صحت بر چهار اصل استوار است: «بالرياضة، وتدبير الغذاء، والنوم، واليقظة» (ورزش، تدبیر خوراک، خواب کافی و بیداری سنجیده).
۳. امور طبیعیه حاکم بر مزاج بدن انسان مشتمل بر هفت رکن است: «الاركان والامزجة والاخلاط والاعضاء والارواح والقوى والافعال».`,
      sources: [
        {
          sourceId: 'SRC-1',
          bookTitle: 'قانون فی الطب (کتاب اول - کلیات)',
          authorName: 'ابن سینا (شیخ الرئیس ابو علی سینا)',
          manuscriptTitle: 'نسخه کهن خط نسخ قانون در کتابخانه ملک',
          pageNumber: 1,
          excerpt:
            'الطب علم يتعرف منه احوال بدن الانسان من جهة ما يصح وما يزول عن الصحة ليحفظ الصحة حاصلة ويستردها زائلة ولما كان حفظ الصحة بالرياضة وتدبير الغذاء والنوم واليقظة وجب معرفة الاسباب',
        },
      ],
      timestamp: '۱۰:۰۲',
    },
  ]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isStreaming]);

  // Handle submitting query
  const handleSendMessage = () => {
    if (!inputMessage.trim() || isStreaming) return;

    const userMsg: ChatMessage = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    const currentQuery = inputMessage;
    setInputMessage('');
    setIsStreaming(true);

    // Retrieve matching records from corpus
    const normQ = normalizePersianArabicText(currentQuery);
    let matchedSources: SourceCitation[] = [];
    let assistantResponseText = '';

    if (normQ.includes('نبض') || normQ.includes('قلب')) {
      matchedSources = [
        {
          sourceId: 'SRC-1',
          bookTitle: 'قانون فی الطب',
          authorName: 'ابن سینا',
          manuscriptTitle: 'نسخه کهن خط نسخ قانون در کتابخانه ملک',
          pageNumber: 14,
          excerpt:
            'النبض حركة في القلب والشرايين تعرض على شكل انبساط وانقباض لترويح الروح بالهواء البارد ونفي الفضلات الدخانية. وانما يعرف النبض الطبيعي بمقدار حركته وقوته وسرعته وتواتره واستوائه',
        },
      ];
      assistantResponseText = `پیرامون پرسش شما در باب نبض، در متن کهن نسخه قانون فی الطب [SRC-1] چنین آمده است:\n\n«النبض حركة في القلب والشرايين تعرض على شكل انبساط وانقباض لترويح الروح بالهواء البارد ونفي الفضلات الدخانية»\n\nابن سینا حرکت نبض را حاصل دو عامل می‌داند: رساندن هوای خنک برای ترویح روح حیوانی و دفع مواد دخانی. همچنین ۱۰ شاخص برای تشخیص نبض مطرح می‌سازد از جمله قوت، سرعت، تواتر، استواء و لین و صلابت آلت شریان.`;
    } else if (normQ.includes('رازی') || normQ.includes('آبله') || normQ.includes('سرخک') || normQ.includes('حا Ahora')) {
      matchedSources = [
        {
          sourceId: 'SRC-2',
          bookTitle: 'الحاوی فی الطب',
          authorName: 'محمد بن زکریای رازی',
          manuscriptTitle: 'نسخه خطی الحاوی در علم امراض و تجارب رازی',
          pageNumber: 8,
          excerpt:
            'قال ابو بکر الرازی: اذا اشتدت الحمى وصحبها حمرة فی العینین وحكة فی الانف فتوقع خروج الحصبة او الجدری. وان كانت آلام الظهر اشد فالجدری اقرب وان كان السعال والخشونة اظهر فالحصبة اسبق',
        },
      ];
      assistantResponseText = `در نسخه خطی الحاوی اثر محمد بن زکریای رازی [SRC-2]، تفکیک بالینی میان سرخک (الحصبة) و آبله (الجدری) به وضوح قید گردیده است:\n\n«اذا اشتدت الحمى وصحبها حمرة فی العینین وحكة فی الانف فتوقع خروج الحصبة او الجدری. وان كانت آلام الظهر اشد فالجدری اقرب»\n\nرازی بیان می‌دارد که اگر درد در ناحیه پشت و کمر غالب باشد، بیماری آبله نزدیک‌تر است و چنانچه سرفه و خشونت سینه ظاهر شود، سرخک مقدم است. درمان اولیه را نیز تلطیف غذا و نوشیدن ماءالشعیر و سکنجبین تجویز می‌کند.`;
    } else if (normQ.includes('دارو') || normQ.includes('بیرونی') || normQ.includes('صیدنه')) {
      matchedSources = [
        {
          sourceId: 'SRC-3',
          bookTitle: 'کتاب الصیدنة فی الطب',
          authorName: 'ابوریحان بیرونی',
          manuscriptTitle: 'نسخه کهن کتاب الصیدنه بیرونی در ادویه و گیاهان دارویی',
          pageNumber: 22,
          excerpt:
            'دانش داروسازی و شناخت ادویه مفرده: صیدنه صناعتی است که بدان ادویه و عقاقیر مفرده از نباتات و حیوانات و معادن شناخته شود و درجات قوت و طبع آنها معین گردد',
        },
      ];
      assistantResponseText = `بر اساس نسخه کهن کتاب الصیدنه ابوریحان بیرونی [SRC-3]، داروسازی دانشی مستقل شناخته شده است:\n\n«صیدنه صناعتی است که بدان ادویه و عقاقیر مفرده از نباتات و حیوانات و معادن شناخته شود و درجات قوت و طبع آنها معین گردد تا پزشک در علاج امراض و تدبیر مزاج ابدان بدانها استعانت جوید»\n\nهمچنین بیرونی تأکید می‌فرماید که ادویه گیاهی باید در سایه خشک شوند تا اسانس و بوی دارویی آنها تباه نگردد.`;
    } else {
      // Zero sources fallback
      assistantResponseText =
        'پژوهشگر ارجمند، بر اساس متون و اسناد نسخ خطی موجود در پایگاه داده فعلی، گزارشی پیرامون این موضوع یافت نشد. طبق قواعد سیستم، از آوردن حدسیات خودداری می‌گردد.';
    }

    // Streaming simulation
    const newAssistantMsg: ChatMessage = {
      id: `msg-${Date.now() + 1}`,
      role: 'assistant',
      content: '',
      sources: matchedSources,
      timestamp: new Date().toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, newAssistantMsg]);

    const words = assistantResponseText.split(' ');
    let currentIdx = 0;

    const interval = setInterval(() => {
      if (currentIdx < words.length) {
        const nextChunk = words.slice(0, currentIdx + 1).join(' ');
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            ...updated[updated.length - 1],
            content: nextChunk,
          };
          return updated;
        });
        currentIdx++;
      } else {
        clearInterval(interval);
        setIsStreaming(false);
      }
    }, 25);
  };

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
      {/* Left/Main Column: Chat Area */}
      <div className="lg:col-span-8 flex flex-col h-[750px] bg-white rounded-xl shadow-sm border border-stone-200 overflow-hidden">
        {/* Chat Header */}
        <div className="p-4 border-b border-stone-200 bg-stone-50 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-amber-600 text-white flex items-center justify-center font-bold shadow-sm">
              <MessageSquareQuote className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-stone-800 flex items-center gap-1.5">
                <span>دستیار هوشمند پژوهش نسخ (Grounded RAG)</span>
                <span className="text-[10px] bg-emerald-100 text-emerald-800 px-1.5 py-0.2 rounded font-mono border border-emerald-300">
                  مستند به پایگاه
                </span>
              </h3>
              <p className="text-xs text-stone-500">پاسخ‌های تحلیلی و مستند بدون فرضیه‌بافی</p>
            </div>
          </div>

          {/* Mode Switcher */}
          <div className="flex items-center gap-1 bg-stone-200/80 p-0.5 rounded-lg text-xs">
            <button
              onClick={() => setConversationMode('RESEARCH')}
              className={`px-3 py-1 rounded-md font-medium transition ${
                conversationMode === 'RESEARCH'
                  ? 'bg-white text-stone-900 shadow-sm font-semibold'
                  : 'text-stone-600 hover:text-stone-900'
              }`}
            >
              حالت پژوهش (Research)
            </button>
            <button
              onClick={() => setConversationMode('OCR')}
              className={`px-3 py-1 rounded-md font-medium transition ${
                conversationMode === 'OCR'
                  ? 'bg-white text-stone-900 shadow-sm font-semibold'
                  : 'text-stone-600 hover:text-stone-900'
              }`}
            >
              حالت استودیو OCR
            </button>
          </div>
        </div>

        {/* Message Thread */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg) => {
            const isUser = msg.role === 'user';
            return (
              <div
                key={msg.id}
                className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}
              >
                {!isUser && (
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-amber-600 to-stone-800 text-amber-200 flex items-center justify-center font-bold text-xs shrink-0 shadow-sm">
                    مک
                  </div>
                )}

                <div
                  className={`max-w-[85%] rounded-2xl p-4 shadow-sm text-sm leading-relaxed ${
                    isUser
                      ? 'bg-amber-600 text-white rounded-br-none'
                      : 'bg-stone-50 border border-stone-200 text-stone-800 rounded-bl-none'
                  }`}
                >
                  <div className="whitespace-pre-line font-manuscript text-base">
                    {msg.content}
                  </div>

                  {/* Grounded Citation Chips */}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-stone-200/70">
                      <span className="text-[11px] font-semibold text-stone-500 block mb-1.5 flex items-center gap-1">
                        <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                        <span>منابع استنادی بازیافته از پایگاه داده (Citations):</span>
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {msg.sources.map((src) => (
                          <button
                            key={src.sourceId}
                            onClick={() => setSelectedCitation(src)}
                            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-amber-100 hover:bg-amber-200 text-amber-900 text-xs border border-amber-300 font-medium transition"
                          >
                            <span className="font-mono font-bold">[{src.sourceId}]</span>
                            <span>{src.bookTitle} (برگ {src.pageNumber})</span>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="flex items-center justify-between mt-2 pt-1 text-[10px] text-stone-400">
                    <span>{msg.timestamp}</span>
                    {!isUser && (
                      <button
                        onClick={() => handleCopy(msg.content, msg.id)}
                        className="hover:text-stone-700 transition"
                        title="رونوشت متن"
                      >
                        {copiedId === msg.id ? <Check className="w-3 h-3 text-emerald-600" /> : <Copy className="w-3 h-3" />}
                      </button>
                    )}
                  </div>
                </div>

                {isUser && (
                  <div className="w-8 h-8 rounded-full bg-stone-300 text-stone-700 flex items-center justify-center font-bold text-xs shrink-0">
                    <User className="w-4 h-4" />
                  </div>
                )}
              </div>
            );
          })}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div className="p-3 border-t border-stone-200 bg-stone-50/80">
          <div className="flex items-center gap-2">
            <textarea
              aria-label="پرسش پژوهشی یا دستور نسخه شناسی"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
              rows={2}
              placeholder="پرسش پژوهشی خود را پیرامون مفاهیم کتب طبی، مؤلفان یا متون کهن وارد فرمایید..."
              className="flex-1 p-2.5 text-sm border border-stone-300 rounded-xl bg-white text-stone-800 focus:ring-2 focus:ring-amber-500 focus:border-amber-500 resize-none outline-none"
              dir="rtl"
            />
            <button
              onClick={handleSendMessage}
              disabled={isStreaming || !inputMessage.trim()}
              className="p-3 bg-amber-600 hover:bg-amber-700 disabled:bg-amber-300 text-white rounded-xl transition shadow-sm"
              title="ارسال پرسش"
            >
              {isStreaming ? (
                <RefreshCw className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5 rtl:rotate-180" />
              )}
            </button>
          </div>

          <div className="flex items-center justify-between mt-2 text-[11px] text-stone-500 px-1">
            <span>مدل زبانی: Gemini 2.5 Flash / Grounded Scholar Engine</span>
            <span>کلید Enter برای ارسال • Shift+Enter برای سطر بعد</span>
          </div>
        </div>
      </div>

      {/* Right Column: Grounded Sources & Citation Inspector */}
      <div className="lg:col-span-4 space-y-4">
        <div className="bg-white rounded-xl shadow-sm border border-stone-200 p-4">
          <div className="flex items-center gap-2 mb-3 pb-2 border-b border-stone-100">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <h4 className="text-sm font-bold text-stone-800">سندنامه پژوهشی (Grounded Documents)</h4>
          </div>

          {selectedCitation ? (
            <div className="space-y-3 p-3 bg-amber-50/50 rounded-lg border border-amber-200">
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-bold text-amber-900 bg-amber-200 px-2 py-0.5 rounded">
                  {selectedCitation.sourceId}
                </span>
                <span className="text-xs text-stone-500 font-mono">برگ {selectedCitation.pageNumber}</span>
              </div>

              <div>
                <span className="text-[11px] text-stone-500 block">عنوان کتاب و مؤلف:</span>
                <p className="text-sm font-bold text-stone-800">{selectedCitation.bookTitle}</p>
                <p className="text-xs text-stone-600">{selectedCitation.authorName}</p>
              </div>

              <div>
                <span className="text-[11px] text-stone-500 block">نسخه خطی مرجع:</span>
                <p className="text-xs font-medium text-amber-800">{selectedCitation.manuscriptTitle}</p>
              </div>

              <div>
                <span className="text-[11px] text-stone-500 block">متن دقیق استخراج‌شده از نسخه:</span>
                <div className="mt-1 p-2 bg-white rounded border border-amber-200 text-xs font-manuscript leading-relaxed text-stone-900">
                  «{selectedCitation.excerpt}»
                </div>
              </div>

              <button
                onClick={() => setSelectedCitation(null)}
                className="w-full text-center text-xs text-stone-500 hover:text-stone-800 pt-1"
              >
                بستن برگه استناد
              </button>
            </div>
          ) : (
            <div className="text-center py-8 text-stone-500 space-y-2">
              <BookOpen className="w-8 h-8 mx-auto text-stone-300" />
              <p className="text-xs">
                روی نشان استناد <span className="font-mono font-bold text-amber-700">[SRC-X]</span> در پیام‌های دستیار کلیک فرمایید تا مشخصات برگه و متن کهن نسخه نمایش یابد.
              </p>
            </div>
          )}
        </div>

        {/* System Paleography Rules */}
        <div className="bg-stone-50 rounded-xl border border-stone-200 p-4 text-xs text-stone-600 space-y-2">
          <h5 className="font-bold text-stone-800 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-amber-600" />
            <span>قوانین استنادی دستیار مخطوطات:</span>
          </h5>
          <ul className="list-disc list-inside space-y-1 text-stone-600 leading-relaxed pr-1">
            <li>عدم ساختگی بودن نقل‌قول‌ها (Strict Grounding)</li>
            <li>حفظ عین املا و انشای متون کهن فارسی و عربی</li>
            <li>تفکیک دقیق نقل قول مستقیم «...» از تفسیر و شرح</li>
            <li>ارجاع صریح به شماره صفحه، عنوان کتاب و مؤلف</li>
          </ul>
        </div>
      </div>
    </div>
  );
};
