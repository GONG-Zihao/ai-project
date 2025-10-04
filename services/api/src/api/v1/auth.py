from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.config import settings
from ...core.security import create_access_token
from ...db.models.user import User
from ...db.session import get_db
from ...repositories import tenants as tenant_repo
from ..deps import authenticate_user
from ...schemas.auth import LoginRequest, Token

router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Token:
    tenant_slug = form_data.scopes[0] if form_data.scopes else "default"
    user = await authenticate_user(db, tenant_slug=tenant_slug, username=form_data.username, password=form_data.password)
    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    expire_at = datetime.now(timezone.utc) + expires_delta
    access_token = create_access_token(
        subject=form_data.username,
        expires_delta=expires_delta,
        additional_claims={"tenant": tenant_slug},
    )
    return Token(access_token=access_token, expires_at=expire_at, tenant=tenant_slug)


@router.post("/login", response_model=Token)
async def login(login_req: LoginRequest, db: AsyncSession = Depends(get_db)) -> Token:
    tenant = await tenant_repo.get_by_slug(db, login_req.tenant_slug)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    user = await authenticate_user(
        db,
        tenant_slug=login_req.tenant_slug,
        username=login_req.username,
        password=login_req.password,
    )
    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    expire_at = datetime.now(timezone.utc) + expires_delta
    access_token = create_access_token(
        subject=user.username,
        expires_delta=expires_delta,
        additional_claims={"tenant": tenant.slug},
    )
    return Token(access_token=access_token, expires_at=expire_at, tenant=tenant.slug)
