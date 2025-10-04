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
        self.orchestrator = orchestrator

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

    async def generate_lesson_plan(
        self,
        *,
        subject: str,
        topic: str,
        objectives: list[str],
        audience: str | None = None,
    ) -> dict[str, Any]:
        sys_prompt = (
            "你是一位资深的教研员，请根据教学目标制定详细的课堂教学方案，包含导入、知识讲解、互动练习和作业布置。"
        )
        objectives_text = "\n".join(f"- {item}" for item in objectives) if objectives else "- 夯实核心知识"
        prompt = (
            f"学科：{subject}\n"
            f"主题：{topic}\n"
            f"教学对象：{audience or '班级学生'}\n"
            f"教学目标：\n{objectives_text}\n"
            "请输出：1) 课堂流程概览 2) 每个环节的时间分配与活动 3) 提供差异化支持建议 4) 课后作业与拓展。"
        )
        response = await self.orchestrator.generate(
            prompt=prompt,
            system_prompt=sys_prompt,
            metadata={"subject": subject, "topic": topic},
        )
        return {
            "outline": response.get("content", ""),
            "provider": response.get("provider", "unknown"),
            "metadata": response.get("metadata", {}),
        }


ai_service = AIService()
