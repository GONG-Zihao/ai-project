from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..core.security import verify_password
from ..db.models.user import User, UserRole
from ..db.session import get_db
from ..repositories import users as user_repo

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def authenticate_user(db: AsyncSession, tenant_slug: str, username: str, password: str) -> User:
    user = await user_repo.get_by_username(db, tenant_slug=tenant_slug, username=username)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User disabled")
    return user


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str | None = payload.get("sub")
        tenant_slug: str | None = payload.get("tenant")
        if username is None or tenant_slug is None:
            raise credentials_exception
    except JWTError as exc:
        raise credentials_exception from exc

    user = await user_repo.get_by_username(db, tenant_slug=tenant_slug, username=username)
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User disabled")
    return user


def require_roles(*roles: UserRole):
    async def role_checker(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if current_user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return current_user

    return role_checker
