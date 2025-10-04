from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from ..db.models.user import UserRole
from .base import ORMModel


class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: UserRole = UserRole.STUDENT


class UserCreate(UserBase):
    password: str
    tenant_slug: str


class UserRead(UserBase, ORMModel):
    id: int
    tenant_id: int
    is_active: bool
    created_at: datetime


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: Optional[UserRole] = None
    password: Optional[str] = None
