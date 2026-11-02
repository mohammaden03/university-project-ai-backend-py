from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.search_repository import SearchRepository
from app.ai.retrieval.hybrid_search import SearchFilter, SearchResultItem
from app.schemas.search import SearchRequest, SearchResponse
from app.utils.text_normalization import PersianArabicNormalizer


class SearchService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SearchRepository(db)

    async def execute_search(self, request: SearchRequest) -> SearchResponse:
        norm_query = PersianArabicNormalizer.normalize_for_search(request.query)

        if request.mode == "lexical":
            results = await self.repo.lexical_search(
                norm_query, filters=request.filters, limit=request.page_size * request.page
            )
        elif request.mode == "semantic":
            results = await self.repo.semantic_search(
                norm_query, filters=request.filters, limit=request.page_size * request.page
            )
        else:
            # Default to hybrid
            results = await self.repo.hybrid_search(
                norm_query, filters=request.filters, limit=request.page_size * request.page
            )

        # Pagination slice
        start_idx = (request.page - 1) * request.page_size
        page_results = results[start_idx : start_idx + request.page_size]

        return SearchResponse(
            query=request.query,
            normalized_query=norm_query,
            total=len(results),
            page=request.page,
            page_size=request.page_size,
            results=page_results,
        )

    async def get_suggestions(self, prefix: str) -> List[str]:
        norm = PersianArabicNormalizer.normalize_for_search(prefix)
        # Fast query suggestions based on classical terms
        terms = [
            "قانون فی الطب",
            "کتاب الحاوی فی الطب",
            "الصیدنه فی الطب",
            "تشریح الاعضاء و عروق",
            "بیان نبض و امزجه",
            "ادویه مفرده و مرکبه",
            "حکمت الاشراق سهروردی",
            "زیج ایلخانی طوسی",
        ]
        return [t for t in terms if norm in PersianArabicNormalizer.normalize_for_search(t)][:5]
