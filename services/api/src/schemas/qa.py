from typing import Any, Optional

from pydantic import BaseModel


class QARequest(BaseModel):
    question: str
    subject: Optional[str] = None
    user_context: dict[str, Any] = {}


class QAResponse(BaseModel):
    answer: str
    provider: str
    citations: list[dict]
    usage: dict[str, Any]
    metadata: dict[str, Any] | None = None
