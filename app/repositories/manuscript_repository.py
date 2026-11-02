import uuid
from typing import List, Optional, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.manuscript import Manuscript
from app.models.manuscript_page import ManuscriptPage
from app.models.book import Book
from app.models.author import Author


class ManuscriptRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_manuscripts(
        self, offset: int = 0, limit: int = 10, language: Optional[str] = None
    ) -> Tuple[List[Manuscript], int]:
        query = select(Manuscript).options(
            selectinload(Manuscript.book),
            selectinload(Manuscript.author),
            selectinload(Manuscript.pages),
        )
        if language:
            query = query.where(Manuscript.language == language)

        total_res = await self.db.execute(select(func.count(Manuscript.id)))
        total = total_res.scalar() or 0

        res = await self.db.execute(query.offset(offset).limit(limit))
        return list(res.scalars().all()), total

    async def get_by_id(self, manuscript_id: uuid.UUID) -> Optional[Manuscript]:
        query = (
            select(Manuscript)
            .options(
                selectinload(Manuscript.book),
                selectinload(Manuscript.author),
                selectinload(Manuscript.pages),
            )
            .where(Manuscript.id == manuscript_id)
        )
        res = await self.db.execute(query)
        return res.scalar_one_or_none()

    async def create(self, manuscript: Manuscript) -> Manuscript:
        self.db.add(manuscript)
        await self.db.flush()
        return manuscript

    async def add_page(self, page: ManuscriptPage) -> ManuscriptPage:
        self.db.add(page)
        await self.db.flush()
        return page

    async def get_page(self, page_id: uuid.UUID) -> Optional[ManuscriptPage]:
        query = (
            select(ManuscriptPage)
            .options(
                selectinload(ManuscriptPage.manuscript),
                selectinload(ManuscriptPage.transcriptions),
            )
            .where(ManuscriptPage.id == page_id)
        )
        res = await self.db.execute(query)
        return res.scalar_one_or_none()
