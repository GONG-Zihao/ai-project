from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.study_session import StudySession


async def create(
    db: AsyncSession,
    *,
    user_id: int,
    start_at: datetime,
    end_at: datetime | None,
    duration_hours: float | None,
    device: str | None,
) -> StudySession:
    session = StudySession(
        user_id=user_id,
        start_at=start_at,
        end_at=end_at,
        duration_hours=duration_hours,
        device=device,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def list_for_user(db: AsyncSession, user_id: int) -> list[StudySession]:
    result = await db.execute(
        select(StudySession).where(StudySession.user_id == user_id).order_by(StudySession.start_at.desc())
    )
    return list(result.scalars())
