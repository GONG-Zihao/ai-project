from __future__ import annotations

from typing import Any

from services.ai.src.orchestrator import LLMOrchestrator
from services.ai.src.pipelines.qa import QAPipeline
from services.ai.src.retrieval_client import RetrievalClient

class AIService:
    def __init__(self) -> None:
        orchestrator = LLMOrchestrator()
        retrieval = RetrievalClient(orchestrator=orchestrator)
        self.qa_pipeline = QAPipeline(orchestrator=orchestrator, retriever=retrieval)

    async def answer_question(
        self,
        *,
        question: str,
        subject: str | None,
        user_context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        result = await self.qa_pipeline.run(
            question=question,
            subject=subject,
            user_context=user_context,
        )
        return {
            "answer": result.answer,
            "provider": result.provider,
            "citations": result.citations,
            "usage": result.usage,
            "metadata": result.metadata,
        }


ai_service = AIService()
