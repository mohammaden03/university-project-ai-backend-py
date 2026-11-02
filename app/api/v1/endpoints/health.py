from typing import Any, Dict
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.config import get_settings

settings = get_settings()
router = APIRouter(tags=["Health & System"])


@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
    }


@router.get("/health/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    db_ok = False
    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    return {
        "status": "ready" if db_ok else "unhealthy",
        "database": "connected" if db_ok else "disconnected",
        "storage": settings.STORAGE_BACKEND,
    }
