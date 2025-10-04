from datetime import datetime
from typing import Optional

from .base import ORMModel


class KnowledgePointRead(ORMModel):
    id: int
    tenant_id: int
    subject: str
    name: str
    description: Optional[str]
    mastery_level: float
    last_reviewed_at: Optional[datetime]
