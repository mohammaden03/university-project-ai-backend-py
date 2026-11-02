from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    RefreshTokenRequest,
    UserRead,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(data: UserRegister, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    user = await auth_service.register(data)
    return user


@router.post("/login", response_model=TokenResponse)
async def login_user(data: UserLogin, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    tokens = await auth_service.login(data)
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    tokens = await auth_service.refresh_token(data.refresh_token)
    return tokens


@router.get("/me", response_model=UserRead)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user
