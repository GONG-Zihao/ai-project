from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.models.user import User, UserRole
from ...db.session import get_db
from ...repositories import tenants as tenant_repo
from ...repositories import users as user_repo
from ...schemas.user import UserCreate, UserRead, UserUpdate
from ..deps import get_current_user

router = APIRouter()


@router.get("/me", response_model=UserRead)
async def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    tenant = await tenant_repo.get_by_slug(db, payload.tenant_slug)
    if tenant is None:
        tenant = await tenant_repo.create(db, name=payload.tenant_slug.title(), slug=payload.tenant_slug)
    existing = await user_repo.get_by_username(db, tenant_slug=tenant.slug, username=payload.username)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
    user = await user_repo.create_user(
        db,
        tenant=tenant,
        username=payload.username,
        password=payload.password,
        role=payload.role,
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
    )
    return user


@router.patch("/me", response_model=UserRead)
async def update_current_user(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    if payload.full_name is not None:
        current_user.full_name = payload.full_name
    if payload.email is not None:
        current_user.email = payload.email
    if payload.phone is not None:
        current_user.phone = payload.phone
    if payload.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Use password reset endpoint")
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user
