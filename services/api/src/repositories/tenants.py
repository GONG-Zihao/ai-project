from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.tenant import Tenant


async def get_by_slug(db: AsyncSession, slug: str) -> Tenant | None:
    result = await db.execute(select(Tenant).where(Tenant.slug == slug))
    return result.scalar_one_or_none()


async def create(db: AsyncSession, *, name: str, slug: str) -> Tenant:
    tenant = Tenant(name=name, slug=slug)
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)
    return tenant


def list_stmt():
    return select(Tenant).order_by(Tenant.name)
