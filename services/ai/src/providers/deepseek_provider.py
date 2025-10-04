from __future__ import annotations

from typing import Any

import httpx

from ai_edu_core import settings
from .base import LLMProvider


class DeepSeekProvider(LLMProvider):
    name = "deepseek"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or settings.deepseek_api_key
        self.base_url = "https://api.deepseek.com/v1"
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=60.0)

    async def generate(
        self,
        *,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 800,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not self.api_key:
            raise RuntimeError("DeepSeek API key not configured")
        headers = {"Authorization": f"Bearer {self.api_key}"}
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": settings.default_llm_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        response = await self._client.post("/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        choice = data["choices"][0]
        return {
            "content": choice["message"]["content"],
            "usage": data.get("usage", {}),
            "provider": self.name,
            "metadata": metadata or {},
        }

    async def embed(self, *, texts: list[str], model: str | None = None) -> list[list[float]]:
        raise NotImplementedError("DeepSeek embedding not yet supported")

    async def warmup(self) -> None:
        # Perform a lightweight request to ensure connectivity
        if not self.api_key:
            return
        try:
            await self._client.get("/models", headers={"Authorization": f"Bearer {self.api_key}"})
        except httpx.HTTPError:
            pass
