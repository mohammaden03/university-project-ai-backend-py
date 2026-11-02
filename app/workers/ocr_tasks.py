import asyncio
import io
import logging
import uuid
from datetime import datetime, timezone
from PIL import Image
from sqlalchemy import select

from app.workers.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.models.ocr_job import OCRJob, OCRJobStatus
from app.models.manuscript_page import ManuscriptPage
from app.models.transcription import Transcription, VerificationStatus
from app.storage.s3_storage import get_storage
from app.ai.ocr.inference import OCRInferenceService
from app.utils.text_normalization import PersianArabicNormalizer

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def process_ocr_job_task(self, job_id_str: str):
    """
    Celery background worker task for async HTR/OCR execution.
    Updates progress, handles errors gracefully, and stores transcription.
    """
    asyncio.run(_async_process_ocr_job(job_id_str))


async def _async_process_ocr_job(job_id_str: str) -> None:
    job_uuid = uuid.UUID(job_id_str)
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(OCRJob).where(OCRJob.id == job_uuid))
        job = result.scalar_one_or_none()
        if not job:
            logger.error(f"OCR Job {job_id_str} not found in database.")
            return

        try:
            job.status = OCRJobStatus.PROCESSING
            job.started_at = datetime.now(timezone.utc)
            job.progress = 0.1
            await session.commit()

            # Read image data via storage abstraction
            storage = get_storage()
            image_bytes = await storage.read(job.uploaded_file_path)
            pil_image = Image.open(io.BytesIO(image_bytes))

            job.progress = 0.4
            await session.commit()

            # Run HTR/OCR inference
            pred_result = OCRInferenceService.run_recognition(pil_image)

            job.progress = 0.8
            await session.commit()

            # Save result onto Job
            job.result = pred_result.model_dump()
            job.status = OCRJobStatus.COMPLETED
            job.progress = 1.0
            job.completed_at = datetime.now(timezone.utc)

            # If associated with a manuscript page, automatically create or link Transcription
            if job.manuscript_page_id:
                norm_text = PersianArabicNormalizer.normalize_for_search(pred_result.text)
                transcription = Transcription(
                    manuscript_page_id=job.manuscript_page_id,
                    original_recognized_text=pred_result.text,
                    corrected_text=None,
                    normalized_text=norm_text,
                    language=pred_result.language,
                    model_name=pred_result.model_name,
                    model_version=pred_result.model_version,
                    confidence_score=pred_result.confidence,
                    recognition_metadata={
                        "warnings": pred_result.warnings,
                        "lines": [l.model_dump() for l in pred_result.lines],
                        "preprocessing": pred_result.preprocessing_metadata,
                    },
                    verification_status=VerificationStatus.PENDING,
                )
                session.add(transcription)

            await session.commit()
            logger.info(f"OCR Job {job_id_str} completed successfully.")

        except Exception as e:
            logger.error(f"OCR Job {job_id_str} failed: {str(e)}")
            job.status = OCRJobStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.now(timezone.utc)
            await session.commit()
            raise e
