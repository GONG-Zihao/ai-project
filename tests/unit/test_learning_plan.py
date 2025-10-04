from datetime import datetime

from services.api.src.services.learning_service import learning_service
from services.api.src.db.models.mistake import Mistake


def test_generate_learning_plan_serialisable():
    mistakes = [
        Mistake(
            id=1,
            user_id=1,
            problem_id=None,
            subject="数学",
            knowledge_tags=["函数"],
            difficulty="困难",
            notes=None,
            metadata=None,
            created_at=datetime.utcnow(),
        )
    ]
    plan = learning_service.generate_learning_plan(mistakes)
    assert plan[0]["knowledge"] == "函数"
    assert plan[0]["difficulty_distribution"]["困难"] == 1
    assert "T" in plan[0]["last_seen"]
