"""Simple data seeding script for local development."""

import asyncio
from datetime import datetime

from ..core.config import settings
from ..db.session import AsyncSessionLocal, Base, engine
from ..repositories import tenants as tenant_repo
from ..repositories import users as user_repo
from ..db.models.user import UserRole


async def seed() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        await user_repo.ensure_default_admin(session)
        tenant = await tenant_repo.get_by_slug(session, "default")
        if tenant:
            existing = await user_repo.get_by_username(session, tenant_slug=tenant.slug, username="student")
            if not existing:
                await user_repo.create_user(
                    session,
                    tenant=tenant,
                    username="student",
                    password="Student@123",
                    role=UserRole.STUDENT,
                    full_name="Demo Student",
                    email="student@example.com",
                    phone="13800138000",
                )


if __name__ == "__main__":
    asyncio.run(seed())
