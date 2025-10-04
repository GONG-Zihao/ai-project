from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..session import Base

if TYPE_CHECKING:
    from .problem import Problem
    from .user import User


class Mistake(Base):
    __tablename__ = "mistakes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    problem_id: Mapped[int | None] = mapped_column(ForeignKey("problems.id", ondelete="SET NULL"))
    subject: Mapped[str | None] = mapped_column(String(64))
    knowledge_tags: Mapped[list[str] | None] = mapped_column(JSON)
    difficulty: Mapped[str | None] = mapped_column(String(32))
    notes: Mapped[str | None] = mapped_column(String(1024))
    metadata: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    user: Mapped[User] = relationship("User", back_populates="mistakes")
    problem: Mapped[Problem | None] = relationship("Problem", back_populates="mistakes")
