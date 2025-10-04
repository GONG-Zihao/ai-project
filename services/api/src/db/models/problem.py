from __future__ import annotations

from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING

from sqlalchemy import ARRAY, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..session import Base

if TYPE_CHECKING:
    from .tenant import Tenant
    from .user import User
    from .mistake import Mistake


class SubjectEnum(str, PyEnum):
    MATH = "数学"
    PHYSICS = "物理"
    CHEMISTRY = "化学"
    ENGLISH = "英语"
    CHINESE = "语文"
    OTHER = "其他"


class Problem(Base):
    __tablename__ = "problems"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    author_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    subject: Mapped[str] = mapped_column(String(32), default=SubjectEnum.OTHER.value)
    knowledge_tags: Mapped[list[str] | None] = mapped_column(ARRAY(String(64)))
    difficulty: Mapped[str | None] = mapped_column(String(32))
    content: Mapped[dict] = mapped_column(JSON, nullable=False)
    answer: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    tenant: Mapped[Tenant] = relationship("Tenant")
    author: Mapped[User | None] = relationship("User")
    mistakes: Mapped[list[Mistake]] = relationship("Mistake", back_populates="problem", cascade="all, delete-orphan")
