import logging
import uuid
from typing import List, Optional
from sqlalchemy import select, func, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.manuscript import Manuscript
from app.models.manuscript_page import ManuscriptPage
from app.models.book import Book
from app.models.author import Author
from app.models.transcription import Transcription
from app.models.embedding import Embedding
from app.ai.embeddings.embedding_service import EmbeddingService
from app.ai.retrieval.hybrid_search import SearchFilter, SearchResultItem, HybridRanker
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SearchRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def hybrid_search(
        self,
        query: str,
        filters: Optional[SearchFilter] = None,
        limit: int = 10,
    ) -> List[SearchResultItem]:
        # 1. Lexical retrieval via PostgreSQL ILIKE / Trigram
        lexical_results = await self.lexical_search(query, filters=filters, limit=limit)

        # 2. Vector semantic retrieval via pgvector
        semantic_results = []
        if settings.VECTOR_SEARCH_ENABLED:
            try:
                semantic_results = await self.semantic_search(query, filters=filters, limit=limit)
            except Exception as e:
                logger.warning(f"Vector search failed, falling back to lexical: {e}")

        # 3. Fuse rankings using Reciprocal Rank Fusion
        fused = HybridRanker.rrf_fuse(lexical_results, semantic_results)
        return fused[:limit]

    async def lexical_search(
        self,
        query: str,
        filters: Optional[SearchFilter] = None,
        limit: int = 10,
    ) -> List[SearchResultItem]:
        search_pattern = f"%{query}%"

        stmt = (
            select(
                Transcription,
                ManuscriptPage,
                Manuscript,
                Book,
                Author,
            )
            .join(ManuscriptPage, Transcription.manuscript_page_id == ManuscriptPage.id)
            .join(Manuscript, ManuscriptPage.manuscript_id == Manuscript.id)
            .outerjoin(Book, Manuscript.book_id == Book.id)
            .outerjoin(Author, Manuscript.author_id == Author.id)
            .where(
                or_(
                    Transcription.normalized_text.ilike(search_pattern),
                    Transcription.original_recognized_text.ilike(search_pattern),
                )
            )
        )

        # Apply metadata filters
        if filters:
            if filters.book_id:
                stmt = stmt.where(Manuscript.book_id == uuid.UUID(filters.book_id))
            if filters.author_id:
                stmt = stmt.where(Manuscript.author_id == uuid.UUID(filters.author_id))
            if filters.manuscript_id:
                stmt = stmt.where(Manuscript.id == uuid.UUID(filters.manuscript_id))
            if filters.page_number:
                stmt = stmt.where(ManuscriptPage.page_number == filters.page_number)
            if filters.language:
                stmt = stmt.where(Manuscript.language == filters.language)
            if filters.script_style:
                stmt = stmt.where(Manuscript.script_style == filters.script_style)

        stmt = stmt.limit(limit)
        result = await self.db.execute(stmt)
        rows = result.all()

        items: List[SearchResultItem] = []
        for tr, page, ms, book, author in rows:
            display_text = tr.display_text
            items.append(
                SearchResultItem(
                    id=str(tr.id),
                    text=display_text,
                    book={"id": str(book.id), "title": book.title} if book else None,
                    author={"id": str(author.id), "name": author.full_name} if author else None,
                    manuscript={
                        "id": str(ms.id),
                        "title": ms.title,
                        "script_style": ms.script_style,
                        "source": ms.source,
                    },
                    page_number=page.page_number,
                    relevance_score=0.85,
                    match_type="lexical",
                )
            )

        return items

    async def semantic_search(
        self,
        query: str,
        filters: Optional[SearchFilter] = None,
        limit: int = 10,
    ) -> List[SearchResultItem]:
        # Generate query vector
        query_vector = EmbeddingService.generate_query_embedding(query)

        # pgvector cosine distance: embedding.cosine_distance(query_vector)
        stmt = (
            select(
                Embedding,
                Transcription,
                ManuscriptPage,
                Manuscript,
                Book,
                Author,
                Embedding.embedding.cosine_distance(query_vector).label("distance"),
            )
            .join(Transcription, Embedding.transcription_id == Transcription.id)
            .join(ManuscriptPage, Embedding.manuscript_page_id == ManuscriptPage.id)
            .join(Manuscript, ManuscriptPage.manuscript_id == Manuscript.id)
            .outerjoin(Book, Manuscript.book_id == Book.id)
            .outerjoin(Author, Manuscript.author_id == Author.id)
        )

        if filters:
            if filters.book_id:
                stmt = stmt.where(Manuscript.book_id == uuid.UUID(filters.book_id))
            if filters.author_id:
                stmt = stmt.where(Manuscript.author_id == uuid.UUID(filters.author_id))
            if filters.manuscript_id:
                stmt = stmt.where(Manuscript.id == uuid.UUID(filters.manuscript_id))
            if filters.page_number:
                stmt = stmt.where(ManuscriptPage.page_number == filters.page_number)
            if filters.language:
                stmt = stmt.where(Manuscript.language == filters.language)
            if filters.script_style:
                stmt = stmt.where(Manuscript.script_style == filters.script_style)

        stmt = stmt.order_by("distance").limit(limit)
        result = await self.db.execute(stmt)
        rows = result.all()

        items: List[SearchResultItem] = []
        for emb, tr, page, ms, book, author, distance in rows:
            # Cosine similarity is 1.0 - distance
            sim_score = max(0.0, min(1.0, 1.0 - float(distance)))
            items.append(
                SearchResultItem(
                    id=str(emb.id),
                    text=emb.chunk_text,
                    book={"id": str(book.id), "title": book.title} if book else None,
                    author={"id": str(author.id), "name": author.full_name} if author else None,
                    manuscript={
                        "id": str(ms.id),
                        "title": ms.title,
                        "script_style": ms.script_style,
                        "source": ms.source,
                    },
                    page_number=page.page_number,
                    relevance_score=round(sim_score, 4),
                    match_type="semantic",
                )
            )

        return items
