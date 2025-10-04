from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .base import ORMModel


class KnowledgePointUpsert(BaseModel):
    subject: str
    name: str
    description: Optional[str] = None
    mastery_level: float = 0.5


class KnowledgePointRead(ORMModel):
    id: int
    tenant_id: int
    subject: str
    name: str
    description: Optional[str]
    mastery_level: float
    last_reviewed_at: Optional[datetime]
