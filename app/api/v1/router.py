from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    manuscripts,
    books,
    authors,
    uploads,
    ocr,
    transcriptions,
    search,
    chat,
    datasets,
    health,
    ai_models,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(manuscripts.router)
api_router.include_router(books.router)
api_router.include_router(authors.router)
api_router.include_router(uploads.router)
api_router.include_router(ocr.router)
api_router.include_router(transcriptions.router)
api_router.include_router(search.router)
api_router.include_router(chat.router)
api_router.include_router(datasets.router)
api_router.include_router(health.router)
api_router.include_router(ai_models.router)
