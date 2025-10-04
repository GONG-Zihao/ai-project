from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.interaction import Interaction


async def create(
    db: AsyncSession,
    *,
    user_id: int,
    subject: str | None,
    prompt: str,
    response: str,
    provider: str | None,
    latency_ms: int | None,
    metadata: dict | None,
) -> Interaction:
    record = Interaction(
        user_id=user_id,
        subject=subject,
        prompt=prompt,
        response=response,
        provider=provider,
        latency_ms=latency_ms,
        metadata=metadata,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def list_for_user(db: AsyncSession, user_id: int, limit: int = 100) -> list[Interaction]:
    result = await db.execute(
        select(Interaction)
        .where(Interaction.user_id == user_id)
        .order_by(Interaction.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars())
