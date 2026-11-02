import asyncio
import logging
import uuid
from sqlalchemy import select

from app.workers.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.models.transcription import Transcription
from app.repositories.transcription_repository import TranscriptionRepository

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def reindex_transcription_task(self, transcription_id_str: str):
    """Celery background worker task to recompute embeddings and reindex a transcription."""
    asyncio.run(_async_reindex_transcription(transcription_id_str))


async def _async_reindex_transcription(transcription_id_str: str) -> None:
    t_uuid = uuid.UUID(transcription_id_str)
    async with AsyncSessionLocal() as session:
        repo = TranscriptionRepository(session)
        transcription = await repo.get_by_id(t_uuid)
        if not transcription:
            logger.error(f"Transcription {transcription_id_str} not found.")
            return

        indexed_chunks = await repo.index_transcription(transcription)
        await session.commit()
        logger.info(f"Reindexed transcription {transcription_id_str} into {indexed_chunks} vector chunks.")
