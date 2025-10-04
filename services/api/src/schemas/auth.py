from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    tenant: Optional[str] = None


class TokenPayload(BaseModel):
    sub: Optional[str]
    exp: Optional[int]
    tenant: Optional[str]


class LoginRequest(BaseModel):
    username: str
    password: str
    tenant_slug: str
