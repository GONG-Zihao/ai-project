from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.models.user import User, UserRole
from ...db.session import get_db
from ...repositories import tenants as tenant_repo
from ...schemas.tenant import TenantCreate, TenantRead
from ..deps import get_current_user, require_roles

router = APIRouter()


@router.get("", response_model=list[TenantRead])
async def list_tenants(
    _: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> list[TenantRead]:
    result = await db.execute(tenant_repo.list_stmt())
    return [TenantRead.model_validate(row) for row in result.scalars()]


@router.post("", response_model=TenantRead, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    payload: TenantCreate,
    _: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> TenantRead:
    existing = await tenant_repo.get_by_slug(db, payload.slug)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tenant already exists")
    tenant = await tenant_repo.create(db, name=payload.name, slug=payload.slug)
    return TenantRead.model_validate(tenant)
