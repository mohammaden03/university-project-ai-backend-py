import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.transcription import Transcription, VerificationStatus
from app.repositories.transcription_repository import TranscriptionRepository
from app.core.exceptions import EntityNotFoundException


class TranscriptionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = TranscriptionRepository(db)

    async def get_transcription(self, transcription_id: uuid.UUID) -> Transcription:
        t = await self.repo.get_by_id(transcription_id)
        if not t:
            raise EntityNotFoundException("Transcription", transcription_id)
        return t

    async def save_correction(
        self, transcription_id: uuid.UUID, corrected_text: str
    ) -> Transcription:
        t = await self.repo.update_correction(transcription_id, corrected_text)
        if not t:
            raise EntityNotFoundException("Transcription", transcription_id)
        return t

    async def verify_transcription(
        self, transcription_id: uuid.UUID, status: VerificationStatus
    ) -> Transcription:
        t = await self.repo.set_verification_status(transcription_id, status)
        if not t:
            raise EntityNotFoundException("Transcription", transcription_id)
        return t

    async def reindex_transcription(self, transcription_id: uuid.UUID) -> int:
        t = await self.get_transcription(transcription_id)
        return await self.repo.index_transcription(t)
