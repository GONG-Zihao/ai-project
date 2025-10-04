from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..session import Base

if TYPE_CHECKING:
    from .classroom import Classroom
    from .user import User


class Enrollment(Base):
    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("classroom_id", "user_id", name="uq_enrollment_class_user"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    classroom_id: Mapped[int] = mapped_column(ForeignKey("classrooms.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(default="student")
    enrolled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    classroom: Mapped[Classroom] = relationship("Classroom", back_populates="enrollments")
    user: Mapped[User] = relationship("User", back_populates="enrollments")
