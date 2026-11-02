import logging
from typing import AsyncGenerator, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.retrieval.hybrid_search import SearchFilter, HybridRanker
from app.ai.retrieval.context_builder import ContextBuilder, GroundedContext
from app.ai.retrieval.reranker import MultilingualReranker
from app.ai.assistant.answer_generator import LLMAnswerGenerator
from app.repositories.search_repository import SearchRepository
from app.utils.text_normalization import PersianArabicNormalizer

logger = logging.getLogger(__name__)


class AssistantEngine:
    """
    Orchestrates the entire RAG pipeline for manuscript research and OCR interaction.
    """

    @classmethod
    async def process_research_query(
        cls,
        query: str,
        db: AsyncSession,
        filters: Optional[SearchFilter] = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
        max_context_passages: int = 5,
    ) -> Dict[str, Any]:
        # 1. Normalize query
        norm_query = PersianArabicNormalizer.normalize_for_search(query)

        # 2. Retrieve candidate passages from PostgreSQL via hybrid search
        search_repo = SearchRepository(db)
        candidates = await search_repo.hybrid_search(
            query=norm_query,
            filters=filters,
            limit=15,
        )

        # 3. Rerank candidate passages
        reranked = MultilingualReranker.rerank(norm_query, candidates, top_k=max_context_passages)

        # 4. Build strict citation context
        grounded_context = ContextBuilder.build_context(reranked, max_passages=max_context_passages)

        # 5. Generate LLM response
        answer_result = await LLMAnswerGenerator.generate_answer(
            query=query,
            grounded_context=grounded_context,
            chat_history=chat_history,
        )

        return answer_result

    @classmethod
    async def stream_research_query(
        cls,
        query: str,
        db: AsyncSession,
        filters: Optional[SearchFilter] = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
        max_context_passages: int = 5,
    ) -> AsyncGenerator[str, None]:
        norm_query = PersianArabicNormalizer.normalize_for_search(query)

        search_repo = SearchRepository(db)
        candidates = await search_repo.hybrid_search(
            query=norm_query,
            filters=filters,
            limit=15,
        )

        reranked = MultilingualReranker.rerank(norm_query, candidates, top_k=max_context_passages)
        grounded_context = ContextBuilder.build_context(reranked, max_passages=max_context_passages)

        async for event in LLMAnswerGenerator.stream_answer(
            query=query,
            grounded_context=grounded_context,
            chat_history=chat_history,
        ):
            yield event
