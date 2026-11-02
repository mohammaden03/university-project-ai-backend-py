import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_researcher
from app.models.user import User
from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate, BookRead
from app.core.exceptions import EntityNotFoundException

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("", response_model=List[BookRead])
async def list_books(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Book).options(selectinload(Book.author)).order_by(Book.title))
    return list(res.scalars().all())


@router.post("", response_model=BookRead, status_code=status.HTTP_201_CREATED)
async def create_book(
    data: BookCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_researcher),
):
    book = Book(
        title=data.title,
        alternative_titles=data.alternative_titles,
        author_id=data.author_id,
        language=data.language,
        description=data.description,
        publication_period=data.publication_period,
    )
    db.add(book)
    await db.flush()
    return book


@router.get("/{id}", response_model=BookRead)
async def get_book(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Book).options(selectinload(Book.author)).where(Book.id == id))
    book = res.scalar_one_or_none()
    if not book:
        raise EntityNotFoundException("Book", id)
    return book


@router.put("/{id}", response_model=BookRead)
async def update_book(
    id: uuid.UUID,
    data: BookUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_researcher),
):
    res = await db.execute(select(Book).where(Book.id == id))
    book = res.scalar_one_or_none()
    if not book:
        raise EntityNotFoundException("Book", id)

    for field, val in data.model_dump(exclude_unset=True).items():
        setattr(book, field, val)

    await db.flush()
    return book


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_researcher),
):
    res = await db.execute(select(Book).where(Book.id == id))
    book = res.scalar_one_or_none()
    if not book:
        raise EntityNotFoundException("Book", id)
    await db.delete(book)
    await db.flush()
