from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..session import Base

if TYPE_CHECKING:
    from .user import User


class StudySession(Base):
    __tablename__ = "study_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duration_hours: Mapped[float | None] = mapped_column(Float)
    device: Mapped[str | None] = mapped_column()

    user: Mapped[User] = relationship("User", back_populates="study_sessions")
