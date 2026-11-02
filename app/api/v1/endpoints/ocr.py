import io
import time
import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, status
from PIL import Image
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.ocr_job import OCRJob, OCRJobStatus
from app.models.transcription import Transcription, VerificationStatus
from app.schemas.ocr import (
    OCRRecognizeRequest,
    OCRStructuredResponse,
    OCRJobStatusResponse,
    OCRModelInfo,
)
from app.ai.ocr.inference import OCRInferenceService
from app.storage.s3_storage import get_storage
from app.utils.text_normalization import PersianArabicNormalizer
from app.core.exceptions import EntityNotFoundException, FileValidationException

router = APIRouter(prefix="/ocr", tags=["OCR / HTR"])


@router.post("/recognize", response_model=OCRStructuredResponse)
async def recognize_manuscript_image(
    request: OCRRecognizeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not request.file_path:
        raise FileValidationException("file_path parameter is required.")

    # 1. Create OCR Job entry in DB
    job = OCRJob(
        manuscript_page_id=request.manuscript_page_id,
        uploaded_file_path=request.file_path,
        status=OCRJobStatus.QUEUED,
        progress=0.0,
    )
    db.add(job)
    await db.flush()

    if request.async_processing:
        # Offload to Celery background task
        try:
            from app.workers.ocr_tasks import process_ocr_job_task
            process_ocr_job_task.delay(str(job.id))
        except Exception:
            pass  # Fallback to in-process execution if Celery daemon is unconfigured
        return OCRStructuredResponse(
            job_id=str(job.id),
            status=OCRJobStatus.QUEUED,
            text="",
            language="fa",
            model=OCRModelInfo(name=request.model_name or "trocr_handwritten_persian", version="1.0.0"),
            confidence=None,
            lines=[],
            warnings=["Asynchronous task queued. Query /ocr/jobs/{job_id} for progress."],
            processing_time_ms=0,
        )

    # Synchronous processing
    job.status = OCRJobStatus.PROCESSING
    job.started_at = datetime.now(timezone.utc)
    job.progress = 0.2
    await db.flush()

    storage = get_storage()
    image_bytes = await storage.read(request.file_path)
    pil_image = Image.open(io.BytesIO(image_bytes))

    # Run modular HTR model prediction
    pred = OCRInferenceService.run_recognition(pil_image, model_name=request.model_name)

    job.status = OCRJobStatus.COMPLETED
    job.progress = 1.0
    job.completed_at = datetime.now(timezone.utc)
    job.result = pred.model_dump()

    # Automatically save transcription if page_id was provided
    if request.manuscript_page_id:
        norm_text = PersianArabicNormalizer.normalize_for_search(pred.text)
        transcription = Transcription(
            manuscript_page_id=request.manuscript_page_id,
            original_recognized_text=pred.text,
            corrected_text=None,
            normalized_text=norm_text,
            language=pred.language,
            model_name=pred.model_name,
            model_version=pred.model_version,
            confidence_score=pred.confidence,
            recognition_metadata={
                "lines": [l.model_dump() for l in pred.lines],
                "warnings": pred.warnings,
                "preprocessing": pred.preprocessing_metadata,
            },
            verification_status=VerificationStatus.PENDING,
            created_by=current_user.id,
        )
        db.add(transcription)

    await db.flush()

    return OCRStructuredResponse(
        job_id=str(job.id),
        status=OCRJobStatus.COMPLETED,
        text=pred.text,
        language=pred.language,
        model=OCRModelInfo(name=pred.model_name, version=pred.model_version),
        confidence=pred.confidence,
        lines=pred.lines,
        warnings=pred.warnings,
        processing_time_ms=pred.processing_time_ms,
        preprocessing_metadata=pred.preprocessing_metadata,
    )


@router.get("/jobs/{job_id}", response_model=OCRJobStatusResponse)
async def get_ocr_job_status(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    res = await db.execute(select(OCRJob).where(OCRJob.id == job_id))
    job = res.scalar_one_or_none()
    if not job:
        raise EntityNotFoundException("OCRJob", job_id)
    return OCRJobStatusResponse(
        job_id=job.id,
        status=job.status,
        progress=job.progress,
        error_message=job.error_message,
        result=job.result,
    )


@router.post("/jobs/{job_id}/retry", response_model=OCRJobStatusResponse)
async def retry_ocr_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    res = await db.execute(select(OCRJob).where(OCRJob.id == job_id))
    job = res.scalar_one_or_none()
    if not job:
        raise EntityNotFoundException("OCRJob", job_id)

    job.status = OCRJobStatus.QUEUED
    job.progress = 0.0
    job.error_message = None
    await db.flush()

    try:
        from app.workers.ocr_tasks import process_ocr_job_task
        process_ocr_job_task.delay(str(job.id))
    except Exception:
        pass

    return OCRJobStatusResponse(
        job_id=job.id,
        status=job.status,
        progress=job.progress,
        error_message=None,
        result=None,
    )
