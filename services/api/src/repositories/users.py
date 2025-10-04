from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.security import hash_password
from ..db.models.tenant import Tenant
from ..db.models.user import User, UserRole
from . import tenants as tenant_repo


async def get_by_username(db: AsyncSession, tenant_slug: str, username: str) -> User | None:
    stmt = (
        select(User)
        .join(Tenant)
        .where(Tenant.slug == tenant_slug)
        .where(User.username == username)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    *,
    tenant: Tenant,
    username: str,
    password: str,
    role: UserRole,
    full_name: str | None,
    email: str | None,
    phone: str | None,
) -> User:
    user = User(
        tenant_id=tenant.id,
        username=username,
        hashed_password=hash_password(password),
        role=role,
        full_name=full_name,
        email=email,
        phone=phone,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def ensure_default_admin(db: AsyncSession) -> None:
    result = await db.execute(select(Tenant).limit(1))
    tenant = result.scalar_one_or_none()
    if tenant is None:
        tenant = await tenant_repo.create(db, name="Default School", slug="default")
    admin = await get_by_username(db, tenant_slug=tenant.slug, username="admin")
    if admin is None:
        await create_user(
            db,
            tenant=tenant,
            username="admin",
            password="Admin@123",
            role=UserRole.ADMIN,
            full_name="Super Admin",
            email="admin@example.com",
            phone=None,
        )
