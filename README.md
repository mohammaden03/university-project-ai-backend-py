# Makhtootat (مخطوطات): Intelligent Manuscript HTR/OCR & Advanced Research Assistant

An enterprise-grade, production-oriented backend and research platform for recognizing, transcribing, organizing, and searching historical Persian and Arabic handwritten manuscripts in traditional Islamic calligraphic scripts (Naskh, Nastaliq, Thuluth, Shikasteh, and Ruqah).

---

## 1. System Features & Workflows

### A. Manuscript Handwritten Text Recognition (HTR/OCR)
- **Multi-format Support**: Ingests TIFF, PNG, JPG, and JPEG historical manuscripts.
- **Image Preprocessing**: CLAHE contrast enhancement, deskewing via contour moment analysis, bilateral denoising preserving delicate ink strokes, and resolution normalization.
- **Line & Region Segmentation**: Horizontal projection profiling preserving right-to-left (RTL) reading order.
- **Model Adapter Architecture**: Compatible with Hugging Face VisionEncoderDecoder architectures (TrOCR), PyLaia, and custom Persian/Arabic HTR models.
- **Confidence Scoring & Warnings**: Token-level logit probabilities with automatic flags for low-confidence ligatures requiring expert paleographer verification.
- **Non-destructive Transcriptions**: Preserves original raw OCR predictions separately from user-submitted corrections.
- **Asynchronous Task Queue**: Celery + Redis workers for background processing of large high-resolution manuscript folios.

### B. Advanced Hybrid Search Engine
- **Multimodal Retrieval**: Combines PostgreSQL full-text search & trigram indexing with pgvector cosine similarity.
- **Scholarly Persian & Arabic Normalization**: Unifies Arabic/Persian Yeh (`ي`, `ى` $\rightarrow$ `ی`) and Kaf (`ك` $\rightarrow$ `ک`), strips Tatweel/Kashida (`ـ`), removes Tashkeel/diacritics, and normalizes Arabic presentation forms while preserving original transcriptions for display.
- **Reciprocal Rank Fusion (RRF)**: Merges lexical rankings with dense multilingual vector embeddings.
- **Metadata Filtering**: Filter by book title, author, manuscript codex, page number, language, and calligraphic script style.

### C. Grounded Scholarly Research Assistant (RAG)
- **Dual Conversation Modes**:
  - `OCR Mode`: Manuscript image upload, transcription review, and correction.
  - `RESEARCH Mode`: Question-answering grounded strictly in indexed manuscript passages.
- **Zero Hallucination Guard**: Never invents folio numbers, authors, or quotations. If no sources exist, explicitly alerts the researcher.
- **Source Citation Badges**: Emits stable reference IDs (`[SRC-1]`) linking directly to the underlying manuscript codex and page.
- **SSE Streaming**: Server-Sent Events delivering real-time tokens (`message_start`, `token`, `source`, `message_complete`).
- **Flexible LLM Backend**: Configurable for Gemini, OpenAI, or a fully offline deterministic citations fallback.

---

## 2. Repository Structure

```text
app/
  main.py                 # FastAPI application, CORS, lifespan, exception handlers
  core/
    config.py             # Pydantic v2 BaseSettings from .env
    database.py           # Async SQLAlchemy 2.0 engine & sessionmaker
    security.py           # Bcrypt hashing & JWT access/refresh tokens
    logging.py            # Structured logging
    exceptions.py         # Domain HTTP exceptions
    dependencies.py       # Auth & role-based access control
  api/
    v1/
      router.py           # Centralized API router
      endpoints/
        auth.py           # Register, login, refresh, me
        manuscripts.py    # Manuscript catalog CRUD
        books.py          # Classical books CRUD
        authors.py        # Authors & alternative names CRUD
        uploads.py        # Authenticated upload & controlled image streaming
        ocr.py            # Sync and async HTR recognition endpoints
        transcriptions.py # Review, correction preservation, verification
        search.py         # Lexical, semantic, and hybrid search
        chat.py           # Conversations and SSE streaming
        datasets.py       # HTR dataset curation and JSONL export
        health.py         # Liveness & readiness probes
        ai_models.py      # Active models & device configuration
  models/                 # SQLAlchemy 2.0 ORM models
    user.py, author.py, book.py, manuscript.py, manuscript_page.py,
    transcription.py, chat.py, chat_message.py, dataset.py, ocr_job.py, embedding.py
  schemas/                # Pydantic v2 validation schemas
  services/               # Business logic & application services
  ai/
    ocr/                  # Preprocessing, line segmentation, TrOCR adapter, confidence
    embeddings/           # Multilingual sentence transformers & chunker
    retrieval/            # Hybrid RRF ranking, reranker, and context builder
    assistant/            # Prompt templates, SSE streaming, and LLM answer generator
  workers/                # Celery app and async background tasks
  repositories/           # Database access layer for search, manuscripts, transcriptions
  storage/                # Local and S3/MinIO storage drivers
  utils/                  # Persian/Arabic normalization, pagination, file validation
migrations/               # Alembic configuration and migration versions
scripts/
  train_htr.py            # PyTorch / HF TrOCR fine-tuning script
  evaluate_cer.py         # Character Error Rate (CER) and Word Error Rate (WER)
  seed_manuscripts.py     # Authentic historical manuscripts seeder
tests/                    # Automated pytest test suites
docker-compose.yml        # Multi-container orchestration (api, worker, postgres, redis)
Dockerfile                # Python 3.12 container specification
requirements.txt          # Python dependencies
.env.example              # Environment variable template
```

---

## 3. Installation & Local Development

### Prerequisites
- Python 3.12+
- PostgreSQL 16+ with `pgvector` and `pg_trgm` extensions
- Redis 7+

### Step 1: Environment Setup
```bash
cp .env.example .env
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Database Migrations
Apply Alembic migrations to set up pgvector, tables, and trigram indexes:
```bash
alembic upgrade head
```

### Step 3: Seed Historical Manuscript Data
Populate documented works from Ibn Sina (Canon of Medicine), Al-Razi (Kitab al-Hawi), and Al-Biruni (Kitab al-Saydanah):
```bash
python scripts/seed_manuscripts.py
```

### Step 4: Run Application & Workers
Start FastAPI dev server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Start Celery background worker:
```bash
celery -A app.workers.celery_app worker --loglevel=info --concurrency=2
```

---

## 4. Docker Deployment

Deploy the entire stack with PostgreSQL (`pgvector`), Redis, FastAPI backend, and Celery worker:

```bash
docker-compose up -d --build
```

Verify services:
```bash
docker-compose ps
curl http://localhost:8000/api/v1/health
```

---

## 5. API Usage Examples

### 1. Hybrid Search
```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "دانش پزشکی در تمدن اسلامی",
    "mode": "hybrid",
    "page": 1,
    "page_size": 5
  }'
```

### 2. OCR Recognition
```bash
curl -X POST "http://localhost:8000/api/v1/ocr/recognize" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "uploads/samples/canon_folio_1.jpg",
    "async_processing": false,
    "enhance_contrast": true
  }'
```

### 3. Stream Research Assistant SSE
```bash
curl -N -X POST "http://localhost:8000/api/v1/chat/conversations/<CONVERSATION_ID>/messages/stream" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "شیخ الرئیس ابن سینا طب را چگونه تعریف کرده است؟"
  }'
```

---

## 6. HTR Model Training & CER Evaluation

Fine-tune a TrOCR vision-encoder-decoder checkpoint on Persian/Arabic manuscript datasets:
```bash
python scripts/train_htr.py \
  --dataset_path ./data/manuscripts_sample.jsonl \
  --output_dir ./models/htr_checkpoints/naskh_v1 \
  --epochs 15 \
  --batch_size 8
```

Evaluate Character Error Rate (CER) and Word Error Rate (WER):
```bash
python scripts/evaluate_cer.py
```

---

## 7. Running Automated Tests

Run the complete test suite with coverage:
```bash
pytest -v --asyncio-mode=auto
```
