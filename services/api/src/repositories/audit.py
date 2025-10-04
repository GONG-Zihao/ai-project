from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.audit_event import AuditEvent


async def log_event(
    db: AsyncSession,
    *,
    tenant_id: int | None,
    user_id: int | None,
    action: str,
    resource: str,
    metadata: dict | None = None,
) -> AuditEvent:
    event = AuditEvent(
        tenant_id=tenant_id,
        user_id=user_id,
        action=action,
        resource=resource,
        metadata=metadata,
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event
