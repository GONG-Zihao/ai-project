from datetime import datetime

from pydantic import BaseModel


class ORMModel(BaseModel):
    class Config:
        from_attributes = True


class TimestampedModel(ORMModel):
    created_at: datetime
