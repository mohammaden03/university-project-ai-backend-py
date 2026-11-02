import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.schemas.auth import UserRegister, UserLogin, TokenResponse
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from app.core.exceptions import AuthenticationException, MakhtootatException
from app.core.config import get_settings

settings = get_settings()


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, data: UserRegister) -> User:
        # Check if email exists
        res = await self.db.execute(select(User).where(User.email == data.email.lower()))
        if res.scalar_one_or_none():
            raise MakhtootatException(status_code=400, detail="A user with this email already exists.")

        user = User(
            full_name=data.full_name,
            email=data.email.lower(),
            hashed_password=get_password_hash(data.password),
            role=data.role or UserRole.USER,
            is_active=True,
        )
        self.db.add(user)
        await self.db.flush()
        return user

    async def login(self, data: UserLogin) -> TokenResponse:
        res = await self.db.execute(select(User).where(User.email == data.email.lower()))
        user = res.scalar_one_or_none()
        if not user or not verify_password(data.password, user.hashed_password):
            raise AuthenticationException("Invalid email or password.")
        if not user.is_active:
            raise AuthenticationException("Account is disabled.")

        access_token = create_access_token(user.id, role=user.role.value)
        refresh_token = create_refresh_token(user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def refresh_token(self, refresh_token_str: str) -> TokenResponse:
        payload = decode_token(refresh_token_str)
        if not payload or payload.get("type") != "refresh":
            raise AuthenticationException("Invalid refresh token.")

        user_id_str = payload.get("sub")
        try:
            user_uuid = uuid.UUID(user_id_str)
        except ValueError:
            raise AuthenticationException("Invalid token subject.")

        res = await self.db.execute(select(User).where(User.id == user_uuid))
        user = res.scalar_one_or_none()
        if not user or not user.is_active:
            raise AuthenticationException("User not found or inactive.")

        new_access = create_access_token(user.id, role=user.role.value)
        new_refresh = create_refresh_token(user.id)

        return TokenResponse(
            access_token=new_access,
            refresh_token=new_refresh,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
