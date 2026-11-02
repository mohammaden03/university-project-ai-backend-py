import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_researcher
from app.models.user import User
from app.schemas.manuscript import (
    ManuscriptCreate,
    ManuscriptUpdate,
    ManuscriptRead,
)
from app.services.manuscript_service import ManuscriptService
from app.utils.pagination import PaginatedResponse

router = APIRouter(prefix="/manuscripts", tags=["Manuscripts"])


@router.get("", response_model=PaginatedResponse[ManuscriptRead])
async def list_manuscripts(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    language: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    service = ManuscriptService(db)
    items, total = await service.list_manuscripts(page=page, page_size=page_size, language=language)
    return PaginatedResponse.create(
        items=[ManuscriptRead.model_validate(m) for m in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=ManuscriptRead, status_code=status.HTTP_201_CREATED)
async def create_manuscript(
    data: ManuscriptCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_researcher),
):
    service = ManuscriptService(db)
    manuscript = await service.create_manuscript(data)
    # Reload with relationships
    return await service.get_manuscript(manuscript.id)


@router.get("/{id}", response_model=ManuscriptRead)
async def get_manuscript(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = ManuscriptService(db)
    manuscript = await service.get_manuscript(id)
    return manuscript


@router.put("/{id}", response_model=ManuscriptRead)
async def update_manuscript(
    id: uuid.UUID,
    data: ManuscriptUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_researcher),
):
    service = ManuscriptService(db)
    manuscript = await service.get_manuscript(id)
    for field, val in data.model_dump(exclude_unset=True).items():
        setattr(manuscript, field, val)
    await db.flush()
    return await service.get_manuscript(id)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_manuscript(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_researcher),
):
    service = ManuscriptService(db)
    manuscript = await service.get_manuscript(id)
    await db.delete(manuscript)
    await db.flush()
