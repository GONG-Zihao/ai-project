from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .base import ORMModel


class TenantCreate(BaseModel):
    name: str
    slug: str


class TenantRead(ORMModel):
    id: int
    name: str
    slug: str
