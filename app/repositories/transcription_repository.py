import uuid
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.transcription import Transcription, VerificationStatus
from app.models.embedding import Embedding
from app.ai.embeddings.embedding_service import EmbeddingService
from app.utils.text_normalization import PersianArabicNormalizer


class TranscriptionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, transcription_id: uuid.UUID) -> Optional[Transcription]:
        query = (
            select(Transcription)
            .options(
                selectinload(Transcription.page),
                selectinload(Transcription.embeddings),
            )
            .where(Transcription.id == transcription_id)
        )
        res = await self.db.execute(query)
        return res.scalar_one_or_none()

    async def create(self, transcription: Transcription) -> Transcription:
        self.db.add(transcription)
        await self.db.flush()
        # Automatically generate embeddings and index
        await self.index_transcription(transcription)
        return transcription

    async def update_correction(
        self, transcription_id: uuid.UUID, corrected_text: str
    ) -> Optional[Transcription]:
        transcription = await self.get_by_id(transcription_id)
        if not transcription:
            return None

        # CRITICAL: Preserve original_recognized_text; only update corrected_text
        transcription.corrected_text = corrected_text
        transcription.normalized_text = PersianArabicNormalizer.normalize_for_search(corrected_text)

        await self.db.flush()
        # Reindex with updated text
        await self.index_transcription(transcription)
        return transcription

    async def set_verification_status(
        self, transcription_id: uuid.UUID, status: VerificationStatus
    ) -> Optional[Transcription]:
        transcription = await self.get_by_id(transcription_id)
        if not transcription:
            return None
        transcription.verification_status = status
        await self.db.flush()
        return transcription

    async def index_transcription(self, transcription: Transcription) -> int:
        """
        Deletes old embeddings for this transcription, generates new chunks + vectors,
        and persists them into the embeddings table.
        """
        # Delete existing embeddings for this transcription
        await self.db.execute(
            delete(Embedding).where(Embedding.transcription_id == transcription.id)
        )

        text_to_index = transcription.display_text
        chunk_embeddings = EmbeddingService.generate_embeddings_for_transcription(text_to_index)

        count = 0
        for chunk, vector in chunk_embeddings:
            emb_record = Embedding(
                transcription_id=transcription.id,
                manuscript_page_id=transcription.manuscript_page_id,
                chunk_index=chunk.chunk_index,
                chunk_text=chunk.text,
                normalized_text=chunk.normalized_text,
                embedding=vector,
                metadata_={
                    "model_name": transcription.model_name,
                    "confidence": transcription.confidence_score,
                },
            )
            self.db.add(emb_record)
            count += 1

        await self.db.flush()
        return count
