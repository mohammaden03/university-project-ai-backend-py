import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from app.ai.ocr.base import RecognizedLine
from app.models.ocr_job import OCRJobStatus


class OCRModelInfo(BaseModel):
    name: str
    version: str


class OCRRecognizeRequest(BaseModel):
    file_path: Optional[str] = None
    manuscript_page_id: Optional[uuid.UUID] = None
    model_name: Optional[str] = None
    async_processing: bool = False
    enhance_contrast: bool = True
    deskew: bool = True


class OCRStructuredResponse(BaseModel):
    job_id: str
    status: OCRJobStatus
    text: str
    language: str
    model: OCRModelInfo
    confidence: Optional[float] = None
    lines: List[RecognizedLine] = []
    warnings: List[str] = []
    processing_time_ms: int = 0
    preprocessing_metadata: Dict[str, Any] = {}


class OCRJobStatusResponse(BaseModel):
    job_id: uuid.UUID
    status: OCRJobStatus
    progress: float
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
