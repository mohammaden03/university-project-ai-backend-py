import uuid
from typing import AsyncGenerator, Optional
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.core.exceptions import AuthenticationException, PermissionDeniedException
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    if not token:
        return None
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        return None
    user_id_str = payload.get("sub")
    if not user_id_str:
        return None
    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        return None

    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        return None
    return user


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not token:
        raise AuthenticationException("Authentication required")
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise AuthenticationException("Invalid or expired authentication token")
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise AuthenticationException("Invalid token payload")
    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise AuthenticationException("Invalid user ID in token")

    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()
    if not user:
        raise AuthenticationException("User no longer exists")
    if not user.is_active:
        raise AuthenticationException("User account is inactive")
    return user


class RoleChecker:
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in self.allowed_roles and current_user.role != UserRole.ADMIN:
            raise PermissionDeniedException(
                f"Operation requires one of the following roles: {[r.value for r in self.allowed_roles]}"
            )
        return current_user


require_researcher = RoleChecker([UserRole.RESEARCHER, UserRole.ADMIN])
require_admin = RoleChecker([UserRole.ADMIN])
