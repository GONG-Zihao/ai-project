from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.enrollment import Enrollment


async def enroll(
    db: AsyncSession,
    *,
    classroom_id: int,
    user_id: int,
    role: str,
) -> Enrollment:
    enrollment = Enrollment(
        classroom_id=classroom_id,
        user_id=user_id,
        role=role,
    )
    db.add(enrollment)
    await db.commit()
    await db.refresh(enrollment)
    return enrollment


async def list_for_classroom(db: AsyncSession, classroom_id: int) -> list[Enrollment]:
    result = await db.execute(
        select(Enrollment).where(Enrollment.classroom_id == classroom_id)
    )
    return list(result.scalars())
