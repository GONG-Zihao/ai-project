from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.classroom import Classroom


async def create(
    db: AsyncSession,
    *,
    tenant_id: int,
    name: str,
    description: str | None,
    teacher_id: int | None,
) -> Classroom:
    classroom = Classroom(
        tenant_id=tenant_id,
        name=name,
        description=description,
        teacher_id=teacher_id,
    )
    db.add(classroom)
    await db.commit()
    await db.refresh(classroom)
    return classroom


async def list_for_tenant(db: AsyncSession, tenant_id: int) -> list[Classroom]:
    result = await db.execute(select(Classroom).where(Classroom.tenant_id == tenant_id))
    return list(result.scalars())


async def get_by_id(db: AsyncSession, classroom_id: int) -> Classroom | None:
    result = await db.execute(select(Classroom).where(Classroom.id == classroom_id))
    return result.scalar_one_or_none()
