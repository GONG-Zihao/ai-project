import asyncio

import pytest

from services.ai.src.orchestrator import LLMOrchestrator


@pytest.mark.asyncio
async def test_orchestrator_mock_fallback(monkeypatch):
    orchestrator = LLMOrchestrator()
    deepseek = orchestrator.get_provider("deepseek")

    async def failing_generate(*args, **kwargs):
        raise RuntimeError("forced failure")

    monkeypatch.setattr(deepseek, "generate", failing_generate, raising=True)
    result = await orchestrator.generate(prompt="测试问题", system_prompt=None, provider="deepseek")
    assert result["provider"] == "mock"
    assert "fallback_error" in result["metadata"]
