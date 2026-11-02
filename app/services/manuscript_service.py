import uuid
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.manuscript import Manuscript
from app.models.manuscript_page import ManuscriptPage
from app.schemas.manuscript import ManuscriptCreate, ManuscriptUpdate
from app.repositories.manuscript_repository import ManuscriptRepository
from app.core.exceptions import EntityNotFoundException


class ManuscriptService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ManuscriptRepository(db)

    async def list_manuscripts(
        self, page: int = 1, page_size: int = 10, language: Optional[str] = None
    ) -> Tuple[List[Manuscript], int]:
        offset = (page - 1) * page_size
        return await self.repo.list_manuscripts(offset=offset, limit=page_size, language=language)

    async def get_manuscript(self, manuscript_id: uuid.UUID) -> Manuscript:
        ms = await self.repo.get_by_id(manuscript_id)
        if not ms:
            raise EntityNotFoundException("Manuscript", manuscript_id)
        return ms

    async def create_manuscript(self, data: ManuscriptCreate) -> Manuscript:
        manuscript = Manuscript(
            title=data.title,
            book_id=data.book_id,
            author_id=data.author_id,
            language=data.language,
            script_style=data.script_style,
            description=data.description,
            source=data.source,
            collection_name=data.collection_name,
            catalog_reference=data.catalog_reference,
        )
        return await self.repo.create(manuscript)

    async def add_page_to_manuscript(
        self, manuscript_id: uuid.UUID, image_path: str, image_metadata: dict, page_number: Optional[int]
    ) -> ManuscriptPage:
        # Check manuscript exists
        await self.get_manuscript(manuscript_id)
        page = ManuscriptPage(
            manuscript_id=manuscript_id,
            page_number=page_number,
            image_path=image_path,
            image_metadata=image_metadata,
            processing_status="PENDING",
        )
        return await self.repo.add_page(page)

    async def get_page(self, page_id: uuid.UUID) -> ManuscriptPage:
        page = await self.repo.get_page(page_id)
        if not page:
            raise EntityNotFoundException("ManuscriptPage", page_id)
        return page
