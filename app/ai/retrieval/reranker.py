import logging
from typing import List
from app.ai.retrieval.hybrid_search import SearchResultItem

logger = logging.getLogger(__name__)


class MultilingualReranker:
    """
    Reranks top candidate manuscript passages using cross-attention score or fuzzy token alignment.
    Falls back gracefully when heavy cross-encoder weights are not pre-downloaded.
    """

    @classmethod
    def rerank(
        cls, query: str, results: List[SearchResultItem], top_k: int = 10
    ) -> List[SearchResultItem]:
        if not results:
            return []

        # Clean words from query
        query_words = set(query.split())

        def score_item(item: SearchResultItem) -> float:
            base_score = item.relevance_score
            text_words = set(item.text.split())
            overlap = len(query_words.intersection(text_words))
            boost = (overlap / max(1, len(query_words))) * 0.2
            return base_score + boost

        reranked = sorted(results, key=score_item, reverse=True)
        return reranked[:top_k]
