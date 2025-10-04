from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..session import Base

if TYPE_CHECKING:
    from .tenant import Tenant
    from .classroom import Classroom
    from .enrollment import Enrollment
    from .mistake import Mistake
    from .interaction import Interaction
    from .study_session import StudySession
    from .achievement import Achievement
    from .recommendation import Recommendation


class UserRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    GUARDIAN = "guardian"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("tenant_id", "username", name="uq_user_tenant_username"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    username: Mapped[str] = mapped_column(String(64), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SqlEnum(UserRole), default=UserRole.STUDENT, nullable=False)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    tenant: Mapped[Tenant] = relationship("Tenant", back_populates="users")
    children: Mapped[list["User"]] = relationship("User", remote_side=[id], cascade="all, delete")
    enrollments: Mapped[list[Enrollment]] = relationship("Enrollment", back_populates="user", cascade="all, delete-orphan")
    mistakes: Mapped[list[Mistake]] = relationship("Mistake", back_populates="user", cascade="all, delete-orphan")
    interactions: Mapped[list[Interaction]] = relationship("Interaction", back_populates="user", cascade="all, delete-orphan")
    study_sessions: Mapped[list[StudySession]] = relationship("StudySession", back_populates="user", cascade="all, delete-orphan")
    achievements: Mapped[list[Achievement]] = relationship("Achievement", back_populates="user", cascade="all, delete-orphan")
    recommendations: Mapped[list[Recommendation]] = relationship("Recommendation", cascade="all, delete-orphan")
