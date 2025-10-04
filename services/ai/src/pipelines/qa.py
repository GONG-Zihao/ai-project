from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List

from ai_edu_core import settings

from ..orchestrator import LLMOrchestrator
from ..prompting.templates import PromptTemplateRegistry
from ..safety import evaluate as safety_evaluate
from ..retrieval_client import RetrievalClient


@dataclass
class QAResult:
    answer: str
    provider: str
    citations: list[dict[str, Any]]
    usage: dict[str, Any]
    metadata: dict[str, Any]


class QAPipeline:
    def __init__(self, orchestrator: LLMOrchestrator | None = None, retriever: RetrievalClient | None = None) -> None:
        self.orchestrator = orchestrator or LLMOrchestrator()
        self.retriever = retriever or RetrievalClient()
        self.prompts = PromptTemplateRegistry()

    async def run(
        self,
        *,
        question: str,
        subject: str | None = None,
        user_context: dict[str, Any] | None = None,
        provider: str | None = None,
    ) -> QAResult:
        related_docs = await self.retriever.search(question)
        context_text = "\n".join(doc["text"] for doc in related_docs)
        system_prompt = self.prompts.get_system_prompt(subject=subject)
        user_prompt = self.prompts.render(question=question, context=context_text, user_context=user_context or {})
        response = await self.orchestrator.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            provider=provider,
            metadata={"subject": subject, "user_context": user_context, "citations": related_docs},
        )
        safety = safety_evaluate(response["content"])
        response.setdefault("metadata", {})["safety"] = safety
        return QAResult(
            answer=response["content"],
            provider=response["provider"],
            usage=response.get("usage", {}),
            citations=related_docs,
            metadata=response.get("metadata", {}),
        )
