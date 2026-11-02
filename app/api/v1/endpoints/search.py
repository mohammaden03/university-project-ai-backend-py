from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user_optional
from app.models.user import User
from app.schemas.search import SearchRequest, SearchResponse
from app.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["Search"])


@router.post("", response_model=SearchResponse)
async def search_manuscripts(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional),
):
    """
    Advanced hybrid search over Persian and Arabic manuscripts:
    Combines PostgreSQL trigram lexical search, metadata filters, and pgvector cosine similarity.
    """
    service = SearchService(db)
    return await service.execute_search(request)


@router.get("/suggestions", response_model=List[str])
async def search_suggestions(
    q: str = Query(..., min_length=1, description="Query prefix"),
    db: AsyncSession = Depends(get_db),
):
    service = SearchService(db)
    return await service.get_suggestions(q)
