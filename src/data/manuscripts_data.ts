export interface ManuscriptPageData {
  id: string;
  manuscriptId: string;
  pageNumber: number;
  imageUrl: string;
  thumbnailUrl: string;
  originalText: string;
  correctedText?: string;
  normalizedText: string;
  language: 'fa' | 'ar';
  scriptStyle: 'Naskh' | 'Nastaliq' | 'Thuluth' | 'Shikasteh' | 'Ruqah';
  confidenceScore: number;
  verificationStatus: 'PENDING' | 'VERIFIED' | 'NEEDS_REVIEW';
  modelName: string;
  modelVersion: string;
  warnings: string[];
  lines: {
    lineIndex: number;
    text: string;
    confidence: number;
    box: { x: number; y: number; width: number; height: number };
  }[];
}

export interface ManuscriptItem {
  id: string;
  title: string;
  authorName: string;
  authorId: string;
  bookTitle: string;
  bookId: string;
  language: 'fa' | 'ar';
  scriptStyle: string;
  century: string;
  source: string;
  collectionName: string;
  catalogReference: string;
  description: string;
  pages: ManuscriptPageData[];
}

export const MANUSCRIPT_COLLECTION: ManuscriptItem[] = [
  {
    id: 'ms-canon-avicenna-01',
    title: 'نسخه کهن خط نسخ قانون در کتابخانه ملک',
    authorName: 'ابن سینا (شیخ الرئیس ابو علی سینا)',
    authorId: 'auth-avicenna',
    bookTitle: 'قانون فی الطب (کتاب اول - کلیات)',
    bookId: 'book-canon',
    language: 'ar',
    scriptStyle: 'Naskh',
    century: 'قرن هفتم هجری (۱۳ میلادی)',
    source: 'کتابخانه و موزه ملی ملک تهران',
    collectionName: 'مجموعه کتب طبی کهن',
    catalogReference: 'کتابخانه ملک - شماره ۴۲۸۱',
    description: 'نسخه بسیار نفیس از کتاب اول قانون در طب ابن سینا با سرلوح مذهب، حواشی شروح طبی، و خط نسخ منقح و با اصالت.',
    pages: [
      {
        id: 'page-canon-01',
        manuscriptId: 'ms-canon-avicenna-01',
        pageNumber: 1,
        imageUrl: 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=1200&q=80',
        thumbnailUrl: 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=400&q=80',
        originalText: `بسم الله الرحمن الرحیم وبه ثقتی
قال الشیخ الرئیس ابو علی الحسین بن عبد الله بن سینا رحمه الله
الطب علم يتعرف منه احوال بدن الانسان من جهة ما يصح وما يزول عن الصحة
ليحفظ الصحة حاصلة ويستردها زائلة
ولما كان حفظ الصحة بالرياضة وتدبير الغذاء والنوم واليقظة وجب معرفة الاسباب
واما الامور الطبيعية فهي سبعة: الاركان والامزجة والاخلاط والاعضاء والارواح والقوى والافعال`,
        correctedText: `بسم الله الرحمن الرحیم وبه ثقتی
قال الشیخ الرئیس ابو علی الحسین بن عبد الله بن سینا رحمه الله
الطب علم يتعرف منه احوال بدن الانسان من جهة ما يصح وما يزول عن الصحة
ليحفظ الصحة حاصلة ويستردها زائلة
ولما كان حفظ الصحة بالرياضة وتدبير الغذاء والنوم واليقظة وجب معرفة الاسباب
واما الامور الطبيعية فهي سبعة: الاركان والامزجة والاخلاط والاعضاء والارواح والقوى والافعال`,
        normalizedText: 'بسم الله الرحمن الرحیم وبه ثقتی قال الشیخ الرئیس ابو علی الحسین بن عبد الله بن سینا رحمه الله الطب علم یتعرف منه احوال بدن الانسان من جهه ما یصح وما یزول عن الصحه لیحفظ الصحه حاصله ویستردها زائله ولما کان حفظ الصحه بالbackground وتدبیر الغذاء والنوم والیقظه وجب معرفه الاسباب واما الامور الطبیعیه فهی سبعه الارکان والامزجه والاخلاط والاعضاء والارواح والقوی والافعال',
        language: 'ar',
        scriptStyle: 'Naskh',
        confidenceScore: 0.94,
        verificationStatus: 'VERIFIED',
        modelName: 'trocr_handwritten_persian',
        modelVersion: '1.0.0',
        warnings: [],
        lines: [
          {
            lineIndex: 1,
            text: 'بسم الله الرحمن الرحیم وبه ثقتی',
            confidence: 0.98,
            box: { x: 15, y: 12, width: 70, height: 8 },
          },
          {
            lineIndex: 2,
            text: 'قال الشیخ الرئیس ابو علی الحسین بن عبد الله بن سینا رحمه الله',
            confidence: 0.95,
            box: { x: 10, y: 24, width: 80, height: 9 },
          },
          {
            lineIndex: 3,
            text: 'الطب علم يتعرف منه احوال بدن الانسان من جهة ما يصح وما يزول عن الصحة',
            confidence: 0.93,
            box: { x: 8, y: 37, width: 84, height: 9 },
          },
          {
            lineIndex: 4,
            text: 'ليحفظ الصحة حاصلة ويستردها زائلة',
            confidence: 0.96,
            box: { x: 20, y: 50, width: 60, height: 9 },
          },
          {
            lineIndex: 5,
            text: 'ولما كان حفظ الصحة بالرياضة وتدبير الغذاء والنوم واليقظة وجب معرفة الاسباب',
            confidence: 0.91,
            box: { x: 8, y: 63, width: 84, height: 9 },
          },
          {
            lineIndex: 6,
            text: 'واما الامور الطبيعية فهي سبعة: الاركان والامزجة والاخلاط والاعضاء والارواح والقوى والافعال',
            confidence: 0.92,
            box: { x: 6, y: 76, width: 88, height: 10 },
          },
        ],
      },
      {
        id: 'page-canon-14',
        manuscriptId: 'ms-canon-avicenna-01',
        pageNumber: 14,
        imageUrl: 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?auto=format&fit=crop&w=1200&q=80',
        thumbnailUrl: 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?auto=format&fit=crop&w=400&q=80',
        originalText: `فصل فی دلالات النبض علی احوال القلب والشرایین
النبض حركة في القلب والشرايين تعرض على شكل انبساط وانقباض
لترويح الروح بالهواء البارد ونفي الفضلات الدخانية
وانما يعرف النبض الطبيعي بمقدار حركته وقوته وسرعته وتواتره واستوائه
فالنبض العظیم یدل علی کثرة الحرارة الغریزیة والحاجة الی الترویح
والنبض الصغیر یدل علی ضعف القوة والبرد فی المزاج`,
        normalizedText: 'فصل فی دلالات النبض علی احوال القلب والشرایین النبض حرکه فی القلب والشرایین تعرض علی شکل انبساط وانقباض لترویح الروح بالهواء البارد ونفی الفضلات الدخانیه وانما یعرف النبض الطبیعی بمقدار حرکته وقوته وسرعته وتواتره واستوائه فالنبض العظیم یدل علی کثره الحراره الغریزیه والحاجه الی الترویح والنبض الصغیر یدل علی ضعف القوه والبرد فی المزاج',
        language: 'ar',
        scriptStyle: 'Naskh',
        confidenceScore: 0.91,
        verificationStatus: 'VERIFIED',
        modelName: 'trocr_handwritten_persian',
        modelVersion: '1.0.0',
        warnings: [],
        lines: [
          {
            lineIndex: 1,
            text: 'فصل فی دلالات النبض علی احوال القلب والشرایین',
            confidence: 0.94,
            box: { x: 14, y: 15, width: 72, height: 9 },
          },
          {
            lineIndex: 2,
            text: 'النبض حركة في القلب والشرايين تعرض على شكل انبساط وانقباض',
            confidence: 0.92,
            box: { x: 8, y: 28, width: 84, height: 9 },
          },
          {
            lineIndex: 3,
            text: 'لترويح الروح بالهواء البارد ونفي الفضلات الدخانية',
            confidence: 0.89,
            box: { x: 12, y: 42, width: 76, height: 9 },
          },
          {
            lineIndex: 4,
            text: 'وانما يعرف النبض الطبيعي بمقدار حركته وقوته وسرعته وتواتره واستوائه',
            confidence: 0.93,
            box: { x: 7, y: 55, width: 86, height: 9 },
          },
          {
            lineIndex: 5,
            text: 'فالنبض العظیم یدل علی کثرة الحرارة الغریزیة والحاجة الی الترویح',
            confidence: 0.9,
            box: { x: 9, y: 68, width: 82, height: 9 },
          },
          {
            lineIndex: 6,
            text: 'والنبض الصغیر یدل علی ضعف القوة والبرد فی المزاج',
            confidence: 0.88,
            box: { x: 15, y: 81, width: 70, height: 9 },
          },
        ],
      },
    ],
  },
  {
    id: 'ms-hawi-razi-02',
    title: 'نسخه خطی الحاوی در علم امراض و تجارب بالینی رازی',
    authorName: 'محمد بن زکریای رازی',
    authorId: 'auth-razi',
    bookTitle: 'الحاوی فی الطب',
    bookId: 'book-hawi',
    language: 'ar',
    scriptStyle: 'Naskh',
    century: 'قرن ششم هجری (۱۲ میلادی)',
    source: 'کتابخانه سلیمانیه استانبول',
    collectionName: 'مجموعه ایاصوفیا',
    catalogReference: 'سلیمانیه - نسخه ۳۵۷۲',
    description: 'کتاب الحاوی جامع‌ترین اثر بالینی رازی، مشتمل بر مشاهدات موردی و تشخیص افتراقی آبله و سرخک.',
    pages: [
      {
        id: 'page-hawi-08',
        manuscriptId: 'ms-hawi-razi-02',
        pageNumber: 8,
        imageUrl: 'https://images.unsplash.com/photo-1516979187457-637abb4f9353?auto=format&fit=crop&w=1200&q=80',
        thumbnailUrl: 'https://images.unsplash.com/photo-1516979187457-637abb4f9353?auto=format&fit=crop&w=400&q=80',
        originalText: `قال ابو بکر الرازی: اذا اشتدت الحمى وصحبها حمرة فی العینین وحكة فی الانف
فتوقع خروج الحصبة او الجدری. وان كانت آلام الظهر اشد فالجدری اقرب
وان كان السعال والخشونة اظهر فالحصبة اسبق
والواجب فی اول الامر تلطیف الغذاء واستعمال ماء الشعیر وسکنجبین بارد
وحفظ البصر بقطور ماء الورد والکزبرة الرطبة دفعا للضرر`,
        normalizedText: 'قال ابو بکر الرازی اذا اشتدت الحمی وصحبها حمره فی العینین وحکه فی الانف فتوقع خروج الحصبه او الجدری وان کانت آلام الظهر اشد فالجدری اقرب وان کان السعال والخشونه اظهر فالحصبه اسبق والواجب فی اول الامر تلطیف الغذاء واستعمال ماء الشعیر وسکنجبین بارد وحفظ البصر بقطور ماء الورد والکزبره الرطبه دفعا للضرر',
        language: 'ar',
        scriptStyle: 'Naskh',
        confidenceScore: 0.89,
        verificationStatus: 'VERIFIED',
        modelName: 'trocr_handwritten_persian',
        modelVersion: '1.0.0',
        warnings: [],
        lines: [
          {
            lineIndex: 1,
            text: 'قال ابو بکر الرازی: اذا اشتدت الحمى وصحبها حمرة فی العینین وحكة فی الانف',
            confidence: 0.91,
            box: { x: 6, y: 14, width: 88, height: 10 },
          },
          {
            lineIndex: 2,
            text: 'فتوقع خروج الحصبة او الجدری. وان كانت آلام الظهر اشد فالجدری اقرب',
            confidence: 0.88,
            box: { x: 8, y: 28, width: 84, height: 10 },
          },
          {
            lineIndex: 3,
            text: 'وان كان السعال والخشونة اظهر فالحصبة اسبق',
            confidence: 0.92,
            box: { x: 18, y: 44, width: 64, height: 10 },
          },
          {
            lineIndex: 4,
            text: 'والواجب فی اول الامر تلطیف الغذاء واستعمال ماء الشعیر وسکنجبین بارد',
            confidence: 0.86,
            box: { x: 7, y: 60, width: 86, height: 10 },
          },
          {
            lineIndex: 5,
            text: 'وحفظ البصر بقطور ماء الورد والکزبرة الرطبة دفعا للضرر',
            confidence: 0.89,
            box: { x: 12, y: 75, width: 76, height: 10 },
          },
        ],
      },
    ],
  },
  {
    id: 'ms-saydanah-biruni-03',
    title: 'ترجمه کهن فارسی کتاب الصیدنه در ادویه مفرده و گیاهان دارویی',
    authorName: 'ابوریحان بیرونی',
    authorId: 'auth-biruni',
    bookTitle: 'کتاب الصیدنة فی الطب',
    bookId: 'book-saydanah',
    language: 'fa',
    scriptStyle: 'Nastaliq',
    century: 'قرن هشتم هجری (۱۴ میلادی)',
    source: 'کتابخانه مرکزی دانشگاه تهران',
    collectionName: 'نسخ خطی کهن داروسازی',
    catalogReference: 'دانشگاه تهران - شماره ۲۰۴۱',
    description: 'ترجمه کهن پارسی ابوبکر بن علی کاسانی غزنوی از کتاب الصیدنه بیرونی، در خواص گیاهان، سنگ‌ها و زهرزدایی.',
    pages: [
      {
        id: 'page-saydanah-22',
        manuscriptId: 'ms-saydanah-biruni-03',
        pageNumber: 22,
        imageUrl: 'https://images.unsplash.com/photo-1461360370896-922624d12aa1?auto=format&fit=crop&w=1200&q=80',
        thumbnailUrl: 'https://images.unsplash.com/photo-1461360370896-922624d12aa1?auto=format&fit=crop&w=400&q=80',
        originalText: `دانش داروسازی و شناخت ادویه مفرده
صیدنه صناعتی است که بدان ادویه و عقاقیر مفرده از نباتات و حیوانات و معادن شناخته شود
و درجات قوت و طبع آنها معین گردد تا پزشک در علاج امراض و تدبیر مزاج ابدان
بدانها استعانت جوید و بیمار را تندرستی بازگرداند
و بهترین ادویه آن است که تازه چیده باشند و در سایه خشک کرده باشند
تا جوهر و قوت بوی آن تباه نگردد.`,
        normalizedText: 'دانش داروسازی و شناخت ادویه مفرده صیدنه صناعتی است که بدان ادویه و عقاقیر مفرده از نباتات و حیوانات و معادن شناخته شود و درجات قوت و طبع انها معین گردد تا پزشک در علاج امراض و تدبیر مزاج ابدان بدانها استعانت جوید و بیمار را تندرستی بازگرداند و بهترین ادویه ان است که تازه چیده باشند و در سایه خشک کرده باشند تا جوهر و قوت بوی ان تباه نگردد',
        language: 'fa',
        scriptStyle: 'Nastaliq',
        confidenceScore: 0.93,
        verificationStatus: 'VERIFIED',
        modelName: 'trocr_handwritten_persian',
        modelVersion: '1.0.0',
        warnings: [],
        lines: [
          {
            lineIndex: 1,
            text: 'دانش داروسازی و شناخت ادویه مفرده',
            confidence: 0.97,
            box: { x: 18, y: 12, width: 64, height: 9 },
          },
          {
            lineIndex: 2,
            text: 'صیدنه صناعتی است که بدان ادویه و عقاقیر مفرده از نباتات و حیوانات و معادن شناخته شود',
            confidence: 0.93,
            box: { x: 6, y: 26, width: 88, height: 10 },
          },
          {
            lineIndex: 3,
            text: 'و درجات قوت و طبع آنها معین گردد تا پزشک در علاج امراض و تدبیر مزاج ابدان',
            confidence: 0.92,
            box: { x: 8, y: 41, width: 84, height: 10 },
          },
          {
            lineIndex: 4,
            text: 'بدانها استعانت جوید و بیمار را تندرستی بازگرداند',
            confidence: 0.95,
            box: { x: 15, y: 55, width: 70, height: 10 },
          },
          {
            lineIndex: 5,
            text: 'و بهترین ادویه آن است که تازه چیده باشند و در سایه خشک کرده باشند',
            confidence: 0.91,
            box: { x: 9, y: 70, width: 82, height: 10 },
          },
          {
            lineIndex: 6,
            text: 'تا جوهر و قوت بوی آن تباه نگردد.',
            confidence: 0.94,
            box: { x: 25, y: 84, width: 50, height: 9 },
          },
        ],
      },
    ],
  },
];
