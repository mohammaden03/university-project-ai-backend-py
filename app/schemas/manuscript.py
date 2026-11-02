import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from app.schemas.book import BookRead
from app.schemas.author import AuthorRead


class ManuscriptBase(BaseModel):
    title: str
    book_id: Optional[uuid.UUID] = None
    author_id: Optional[uuid.UUID] = None
    language: str = "fa"
    script_style: Optional[str] = "Naskh"
    description: Optional[str] = None
    source: str
    collection_name: Optional[str] = None
    catalog_reference: Optional[str] = None


class ManuscriptCreate(ManuscriptBase):
    pass


class ManuscriptUpdate(BaseModel):
    title: Optional[str] = None
    book_id: Optional[uuid.UUID] = None
    author_id: Optional[uuid.UUID] = None
    language: Optional[str] = None
    script_style: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = None
    collection_name: Optional[str] = None
    catalog_reference: Optional[str] = None


class ManuscriptPageBase(BaseModel):
    page_number: Optional[int] = None
    image_path: str
    image_metadata: Dict[str, Any] = {}
    processing_status: str = "PENDING"


class ManuscriptPageCreate(BaseModel):
    page_number: Optional[int] = None


class ManuscriptPageRead(ManuscriptPageBase):
    id: uuid.UUID
    manuscript_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ManuscriptRead(ManuscriptBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    book: Optional[BookRead] = None
    author: Optional[AuthorRead] = None
    pages: List[ManuscriptPageRead] = []

    class Config:
        from_attributes = True
