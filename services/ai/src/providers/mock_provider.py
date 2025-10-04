from __future__ import annotations

import random
from typing import Any

from .base import LLMProvider


class MockProvider(LLMProvider):
    name = "mock"

    async def generate(
        self,
        *,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 800,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "content": f"[MOCK RESPONSE]\nSystem: {system_prompt}\nPrompt: {prompt[:200]}",
            "usage": {"prompt_tokens": len(prompt.split()), "completion_tokens": 50},
            "provider": self.name,
            "metadata": metadata or {},
        }

    async def embed(self, *, texts: list[str], model: str | None = None) -> list[list[float]]:
        random.seed(42)
        return [[random.random() for _ in range(10)] for _ in texts]
