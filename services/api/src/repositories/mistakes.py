from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.mistake import Mistake


async def create(
    db: AsyncSession,
    *,
    user_id: int,
    problem_id: int | None,
    subject: str | None,
    knowledge_tags: list[str] | None,
    difficulty: str | None,
    notes: str | None,
    metadata: dict | None,
) -> Mistake:
    mistake = Mistake(
        user_id=user_id,
        problem_id=problem_id,
        subject=subject,
        knowledge_tags=knowledge_tags,
        difficulty=difficulty,
        notes=notes,
        metadata=metadata,
    )
    db.add(mistake)
    await db.commit()
    await db.refresh(mistake)
    return mistake


async def list_for_user(db: AsyncSession, user_id: int) -> list[Mistake]:
    result = await db.execute(select(Mistake).where(Mistake.user_id == user_id).order_by(Mistake.created_at.desc()))
    return list(result.scalars())
