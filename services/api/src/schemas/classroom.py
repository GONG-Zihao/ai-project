from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .base import ORMModel


class ClassroomCreate(BaseModel):
    name: str
    description: Optional[str] = None
    teacher_id: Optional[int] = None


class ClassroomRead(ORMModel):
    id: int
    tenant_id: int
    name: str
    description: Optional[str]
    teacher_id: Optional[int]
    created_at: datetime


class EnrollmentRequest(BaseModel):
    user_id: int
    role: str = "student"
