from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta
from typing import Iterable

from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.mistake import Mistake
from ..db.models.study_session import StudySession
from ..repositories import enrollments as enrollment_repo
from ..repositories import interactions as interaction_repo
from ..repositories import knowledge as knowledge_repo
from ..repositories import mistakes as mistakes_repo
from ..repositories import study_sessions as study_repo


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

    async def user_progress_metrics(self, db: AsyncSession, user_id: int) -> dict:
        interactions = await interaction_repo.list_for_user(db, user_id=user_id, limit=None)
        daily_counter: Counter[str] = Counter()
        subject_counter: Counter[str] = Counter()
        for item in interactions:
            day = item.created_at.date().isoformat() if item.created_at else datetime.utcnow().date().isoformat()
            daily_counter[day] += 1
            subject_counter[item.subject or "其他"] += 1

        sessions = await study_repo.list_for_user(db, user_id=user_id)
        session_series = [
            {
                "start_at": session.start_at.isoformat(),
                "end_at": session.end_at.isoformat() if session.end_at else None,
                "duration_hours": session.duration_hours or 0,
            }
            for session in sessions
        ]

        return {
            "daily_activity": sorted(
                ( {"date": date, "count": count} for date, count in daily_counter.items() ),
                key=lambda entry: entry["date"],
            ),
            "subject_distribution": [
                {"subject": subject, "count": count}
                for subject, count in subject_counter.items()
            ],
            "study_sessions": session_series,
        }

    async def achievements_for_user(self, db: AsyncSession, user_id: int) -> dict:
        mistakes = await mistakes_repo.list_for_user(db, user_id=user_id)
        interactions = await interaction_repo.list_for_user(db, user_id=user_id, limit=None)
        total_mistakes = len(mistakes)
        total_interactions = len(interactions)

        dates = {interaction.created_at.date() for interaction in interactions if interaction.created_at}
        streak = 0
        current_date = datetime.utcnow().date()
        while current_date in dates:
            streak += 1
            current_date = current_date - timedelta(days=1)

        achievements = []
        if total_mistakes >= 10:
            achievements.append({"name": "错题收集者", "level": "bronze"})
        if total_mistakes >= 50:
            achievements.append({"name": "错题大师", "level": "silver"})
        if total_mistakes >= 100:
            achievements.append({"name": "错题王者", "level": "gold"})

        if streak >= 3:
            achievements.append({"name": "坚持不懈", "level": "bronze", "streak": streak})
        if streak >= 7:
            achievements.append({"name": "学习达人", "level": "silver", "streak": streak})
        if streak >= 30:
            achievements.append({"name": "学习王者", "level": "gold", "streak": streak})

        return {
            "totals": {
                "mistakes": total_mistakes,
                "interactions": total_interactions,
                "streak": streak,
            },
            "achievements": achievements,
        }

    async def classroom_dashboard(self, db: AsyncSession, classroom_id: int) -> dict:
        enrollments = await enrollment_repo.list_for_classroom(db, classroom_id=classroom_id)
        student_ids = [record.user_id for record in enrollments]
        subject_counter: Counter[str] = Counter()
        activity: list[dict[str, str]] = []
        total_interactions = 0
        total_mistakes = 0

        for student_id in student_ids:
            interactions = await interaction_repo.list_for_user(db, user_id=student_id, limit=None)
            total_interactions += len(interactions)
            for item in interactions:
                subject_counter[item.subject or "其他"] += 1
                if item.created_at:
                    activity.append({
                        "user_id": student_id,
                        "time": item.created_at.isoformat(),
                        "subject": item.subject or "其他",
                    })
            mistakes = await mistakes_repo.list_for_user(db, user_id=student_id)
            total_mistakes += len(mistakes)

        return {
            "student_count": len(student_ids),
            "total_interactions": total_interactions,
            "total_mistakes": total_mistakes,
            "subject_distribution": [
                {"subject": subject, "count": count}
                for subject, count in subject_counter.items()
            ],
            "recent_activity": sorted(activity, key=lambda item: item["time"], reverse=True)[:20],
        }


learning_service = LearningAnalyticsService()
