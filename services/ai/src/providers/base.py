from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    name: str

    @abstractmethod
    async def generate(
        self,
        *,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 800,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate a model response."""

    @abstractmethod
    async def embed(
        self,
        *,
        texts: list[str],
        model: str | None = None,
    ) -> list[list[float]]:
        """Compute embeddings for given texts."""

    async def warmup(self) -> None:
        """Optional warm-up hook."""
        return None
