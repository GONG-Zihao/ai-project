from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .base import ORMModel


class StudySessionCreate(BaseModel):
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    duration_hours: Optional[float] = None
    device: Optional[str] = None


class StudySessionRead(ORMModel):
    id: int
    user_id: int
    start_at: datetime
    end_at: Optional[datetime]
    duration_hours: Optional[float]
    device: Optional[str]
