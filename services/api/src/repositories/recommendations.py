from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.recommendation import Recommendation


async def create(
    db: AsyncSession,
    *,
    user_id: int,
    recommendation_type: str,
    candidate_id: str,
    payload: dict | None = None,
) -> Recommendation:
    rec = Recommendation(
        user_id=user_id,
        recommendation_type=recommendation_type,
        candidate_id=candidate_id,
        payload=payload,
    )
    db.add(rec)
    await db.commit()
    await db.refresh(rec)
    return rec


async def list_for_user(db: AsyncSession, user_id: int, limit: int = 10) -> list[Recommendation]:
    result = await db.execute(
        select(Recommendation)
        .where(Recommendation.user_id == user_id)
        .order_by(Recommendation.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars())
