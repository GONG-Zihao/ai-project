from __future__ import annotations

from typing import Any

from openai import AsyncOpenAI

from ai_edu_core import settings
from .base import LLMProvider


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self, api_key: str | None = None) -> None:
        self._client = AsyncOpenAI(api_key=api_key or settings.openai_api_key)

    async def generate(
        self,
        *,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 800,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        response = await self._client.chat.completions.create(
            model=settings.default_llm_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        choice = response.choices[0]
        return {
            "content": choice.message.content,
            "usage": response.usage.model_dump() if hasattr(response.usage, "model_dump") else response.usage,
            "provider": self.name,
            "metadata": metadata or {},
        }

    async def embed(self, *, texts: list[str], model: str | None = None) -> list[list[float]]:
        embedding_model = model or "text-embedding-3-small"
        response = await self._client.embeddings.create(
            model=embedding_model,
            input=texts,
        )
        return [item.embedding for item in response.data]
