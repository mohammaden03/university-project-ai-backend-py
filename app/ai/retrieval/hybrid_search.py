from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class SearchFilter(BaseModel):
    book_id: Optional[str] = None
    author_id: Optional[str] = None
    manuscript_id: Optional[str] = None
    page_number: Optional[int] = None
    language: Optional[str] = None
    script_style: Optional[str] = None


class SearchResultItem(BaseModel):
    id: str
    text: str
    book: Optional[Dict[str, Any]] = None
    author: Optional[Dict[str, Any]] = None
    manuscript: Dict[str, Any]
    page_number: Optional[int] = None
    relevance_score: float
    match_type: str  # "semantic", "lexical", "hybrid"


class HybridSearchResponse(BaseModel):
    query: str
    normalized_query: str
    total: int
    page: int
    page_size: int
    results: List[SearchResultItem]


class HybridRanker:
    """
    Combines Lexical (PostgreSQL trigram / FTS) and Semantic (pgvector cosine) results
    using Reciprocal Rank Fusion (RRF) and normalized score weighting.
    """

    @classmethod
    def rrf_fuse(
        cls,
        lexical_items: List[SearchResultItem],
        semantic_items: List[SearchResultItem],
        k: int = 60,
        lexical_weight: float = 0.5,
        semantic_weight: float = 0.5,
    ) -> List[SearchResultItem]:
        scores: Dict[str, float] = {}
        item_map: Dict[str, SearchResultItem] = {}

        # Process Lexical rankings
        for rank, item in enumerate(lexical_items):
            scores[item.id] = scores.get(item.id, 0.0) + lexical_weight * (1.0 / (k + rank + 1))
            item_map[item.id] = item

        # Process Semantic rankings
        for rank, item in enumerate(semantic_items):
            scores[item.id] = scores.get(item.id, 0.0) + semantic_weight * (1.0 / (k + rank + 1))
            if item.id in item_map:
                # Upgraded to hybrid match
                item_map[item.id].match_type = "hybrid"
            else:
                item_map[item.id] = item

        # Sort by fused score
        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        fused_results: List[SearchResultItem] = []
        for sid in sorted_ids:
            item = item_map[sid]
            # Normalize score to [0, 1] range
            item.relevance_score = round(scores[sid] * (k + 1), 4)
            fused_results.append(item)

        return fused_results
