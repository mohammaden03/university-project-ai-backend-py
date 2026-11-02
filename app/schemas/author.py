import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class AuthorBase(BaseModel):
    full_name: str
    alternative_names: Optional[List[str]] = None
    biography: Optional[str] = None
    birth_date: Optional[str] = None
    death_date: Optional[str] = None


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(BaseModel):
    full_name: Optional[str] = None
    alternative_names: Optional[List[str]] = None
    biography: Optional[str] = None
    birth_date: Optional[str] = None
    death_date: Optional[str] = None


class AuthorRead(AuthorBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
