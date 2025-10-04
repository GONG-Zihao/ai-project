from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Iterable

from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.mistake import Mistake
from ..db.models.study_session import StudySession
from ..repositories import study_sessions as study_repo
from ..repositories import knowledge as knowledge_repo
from ..repositories import mistakes as mistakes_repo


class LearningAnalyticsService:
    """Generate adaptive learning insights based on mistake histories."""

    async def update_knowledge_mastery(self, db: AsyncSession, user_id: int, tenant_id: int) -> None:
        mistakes = await mistakes_repo.list_for_user(db, user_id=user_id)
        knowledge_counter = Counter()
        subject_map: dict[str, str] = {}
        for mistake in mistakes:
            for tag in (mistake.knowledge_tags or []):
                knowledge_counter[tag] += 1
                subject_map[tag] = mistake.subject or "其他"
        total = sum(knowledge_counter.values()) or 1
        for tag, count in knowledge_counter.items():
            mastery = max(0.1, 1.0 - (count / total))
            await knowledge_repo.upsert(
                db,
                tenant_id=tenant_id,
                subject=subject_map.get(tag, "其他"),
                name=tag,
                mastery_level=mastery,
            )

    def generate_learning_plan(self, mistakes: Iterable[Mistake]) -> list[dict]:
        grouped: dict[str, list[Mistake]] = {}
        for mistake in mistakes:
            for tag in mistake.knowledge_tags or ["未标注"]:
                grouped.setdefault(tag, []).append(mistake)
        plan = []
        for tag, items in grouped.items():
            difficulty_counts = Counter(item.difficulty or "未标注" for item in items)
            plan.append(
                {
                    "knowledge": tag,
                    "tasks": len(items),
                    "difficulty_distribution": dict(difficulty_counts),
                    "last_seen": max(item.created_at for item in items).isoformat(),
                }
            )
        plan.sort(key=lambda item: item["tasks"], reverse=True)
        return plan

    async def classroom_overview(self, db: AsyncSession, user_id: int) -> dict:
        sessions = await study_repo.list_for_user(db, user_id=user_id)
        total_duration = sum(session.duration_hours or 0 for session in sessions)
        last_session = max((session.start_at for session in sessions), default=None)
        return {
            "total_sessions": len(sessions),
            "total_hours": round(total_duration, 2),
            "last_session": last_session.isoformat() if last_session else None,
        }


learning_service = LearningAnalyticsService()
