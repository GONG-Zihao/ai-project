from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.knowledge_point import KnowledgePoint


async def upsert(
    db: AsyncSession,
    *,
    tenant_id: int,
    subject: str,
    name: str,
    mastery_level: float,
    description: str | None = None,
) -> KnowledgePoint:
    stmt = select(KnowledgePoint).where(
        KnowledgePoint.tenant_id == tenant_id,
        KnowledgePoint.subject == subject,
        KnowledgePoint.name == name,
    )
    result = await db.execute(stmt)
    point = result.scalar_one_or_none()
    if point is None:
        point = KnowledgePoint(
            tenant_id=tenant_id,
            subject=subject,
            name=name,
            mastery_level=mastery_level,
            description=description,
        )
        db.add(point)
    else:
        point.mastery_level = mastery_level
        if description is not None:
            point.description = description
    await db.commit()
    await db.refresh(point)
    return point


async def list_for_tenant(db: AsyncSession, tenant_id: int, subject: str | None = None) -> list[KnowledgePoint]:
    stmt = select(KnowledgePoint).where(KnowledgePoint.tenant_id == tenant_id)
    if subject:
        stmt = stmt.where(KnowledgePoint.subject == subject)
    result = await db.execute(stmt.order_by(KnowledgePoint.mastery_level.desc()))
    return list(result.scalars())
