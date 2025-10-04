from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Dict

from ai_edu_core import settings

from .providers import DeepSeekProvider, LLMProvider, MockProvider, OpenAIProvider


class LLMOrchestrator:
    """Route requests to configured providers with fallbacks."""

    def __init__(self, providers: Mapping[str, LLMProvider] | None = None) -> None:
        self._providers: Dict[str, LLMProvider] = {}
        if providers:
            self._providers.update(providers)
        else:
            self._providers = {
                "deepseek": DeepSeekProvider(),
                "openai": OpenAIProvider(),
                "mock": MockProvider(),
            }

    def get_provider(self, name: str | None = None) -> LLMProvider:
        key = name or settings.default_llm_provider
        if key not in self._providers:
            raise ValueError(f"Provider '{key}' not configured")
        return self._providers[key]

    async def generate(
        self,
        *,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 800,
        provider: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        llm = self.get_provider(provider)
        try:
            return await llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                metadata=metadata,
            )
        except Exception as first_error:
            # Fallback to mock provider only if configured to do so
            if settings.enable_mock_ai or provider == "mock":
                raise
            mock = self.get_provider("mock")
            return await mock.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                metadata={"fallback_error": str(first_error), **(metadata or {})},
            )

    async def embed(
        self,
        *,
        texts: list[str],
        provider: str | None = None,
        model: str | None = None,
    ) -> list[list[float]]:
        llm = self.get_provider(provider)
        try:
            return await llm.embed(texts=texts, model=model)
        except NotImplementedError:
            fallback = self.get_provider("openai")
            return await fallback.embed(texts=texts, model=model)
