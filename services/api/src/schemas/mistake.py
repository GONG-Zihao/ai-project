from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from .base import ORMModel


class MistakeCreate(BaseModel):
    problem_id: Optional[int] = None
    subject: Optional[str] = None
    knowledge_tags: Optional[List[str]] = None
    difficulty: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[dict] = None


class MistakeRead(ORMModel):
    id: int
    user_id: int
    problem_id: Optional[int]
    subject: Optional[str]
    knowledge_tags: Optional[List[str]]
    difficulty: Optional[str]
    notes: Optional[str]
    metadata: Optional[dict]
    created_at: datetime
