import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel
from app.models.transcription import VerificationStatus


class TranscriptionUpdate(BaseModel):
    corrected_text: str


class TranscriptionVerifyRequest(BaseModel):
    status: VerificationStatus


class TranscriptionRead(BaseModel):
    id: uuid.UUID
    manuscript_page_id: uuid.UUID
    original_recognized_text: str
    corrected_text: Optional[str] = None
    normalized_text: str
    language: str
    model_name: str
    model_version: str
    confidence_score: Optional[float] = None
    recognition_metadata: Dict[str, Any] = {}
    verification_status: VerificationStatus
    created_by: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
