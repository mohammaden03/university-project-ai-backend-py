from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.ai.retrieval.hybrid_search import SearchFilter, SearchResultItem


class SearchRequest(BaseModel):
    query: str
    mode: str = Field(default="hybrid", description="Search mode: hybrid, lexical, semantic")
    filters: Optional[SearchFilter] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)


class SearchResponse(BaseModel):
    query: str
    normalized_query: str
    total: int
    page: int
    page_size: int
    results: List[SearchResultItem]
