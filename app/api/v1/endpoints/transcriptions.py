import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_researcher
from app.models.user import User
from app.schemas.transcription import (
    TranscriptionRead,
    TranscriptionUpdate,
    TranscriptionVerifyRequest,
)
from app.services.transcription_service import TranscriptionService

router = APIRouter(prefix="/transcriptions", tags=["Transcriptions"])


@router.get("/{id}", response_model=TranscriptionRead)
async def get_transcription(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TranscriptionService(db)
    return await service.get_transcription(id)


@router.put("/{id}", response_model=TranscriptionRead)
async def update_transcription_correction(
    id: uuid.UUID,
    data: TranscriptionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Saves a scholar's corrected transcription without overwriting the original recognition result.
    Automatically recalculates normalized text and updates pgvector embeddings.
    """
    service = TranscriptionService(db)
    return await service.save_correction(id, data.corrected_text)


@router.post("/{id}/verify", response_model=TranscriptionRead)
async def verify_transcription(
    id: uuid.UUID,
    data: TranscriptionVerifyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_researcher),
):
    """Marks transcription as VERIFIED, PENDING, or NEEDS_REVIEW."""
    service = TranscriptionService(db)
    return await service.verify_transcription(id, data.status)


@router.post("/{id}/reindex")
async def reindex_transcription(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_researcher),
):
    """Triggers re-chunking and embedding re-generation in pgvector."""
    service = TranscriptionService(db)
    chunks_count = await service.reindex_transcription(id)
    return {
        "status": "success",
        "transcription_id": str(id),
        "indexed_chunks": chunks_count,
    }
