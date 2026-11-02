import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_researcher
from app.models.user import User
from app.models.author import Author
from app.schemas.author import AuthorCreate, AuthorUpdate, AuthorRead
from app.core.exceptions import EntityNotFoundException

router = APIRouter(prefix="/authors", tags=["Authors"])


@router.get("", response_model=List[AuthorRead])
async def list_authors(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Author).order_by(Author.full_name))
    return list(res.scalars().all())


@router.post("", response_model=AuthorRead, status_code=status.HTTP_201_CREATED)
async def create_author(
    data: AuthorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_researcher),
):
    author = Author(
        full_name=data.full_name,
        alternative_names=data.alternative_names,
        biography=data.biography,
        birth_date=data.birth_date,
        death_date=data.death_date,
    )
    db.add(author)
    await db.flush()
    return author


@router.get("/{id}", response_model=AuthorRead)
async def get_author(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Author).where(Author.id == id))
    author = res.scalar_one_or_none()
    if not author:
        raise EntityNotFoundException("Author", id)
    return author


@router.put("/{id}", response_model=AuthorRead)
async def update_author(
    id: uuid.UUID,
    data: AuthorUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_researcher),
):
    res = await db.execute(select(Author).where(Author.id == id))
    author = res.scalar_one_or_none()
    if not author:
        raise EntityNotFoundException("Author", id)

    for field, val in data.model_dump(exclude_unset=True).items():
        setattr(author, field, val)

    await db.flush()
    return author


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_author(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_researcher),
):
    res = await db.execute(select(Author).where(Author.id == id))
    author = res.scalar_one_or_none()
    if not author:
        raise EntityNotFoundException("Author", id)
    await db.delete(author)
    await db.flush()
