import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.schemas.author import AuthorRead


class BookBase(BaseModel):
    title: str
    alternative_titles: Optional[List[str]] = None
    author_id: Optional[uuid.UUID] = None
    language: str = "fa"
    description: Optional[str] = None
    publication_period: Optional[str] = None


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = None
    alternative_titles: Optional[List[str]] = None
    author_id: Optional[uuid.UUID] = None
    language: Optional[str] = None
    description: Optional[str] = None
    publication_period: Optional[str] = None


class BookRead(BookBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    author: Optional[AuthorRead] = None

    class Config:
        from_attributes = True
