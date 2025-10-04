from __future__ import annotations

from celery import Celery

from ai_edu_core import settings

celery_app = Celery(
    "ai_edu_worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_routes={
        "services.worker.src.tasks.ocr.extract_text": {"queue": "ocr"},
        "services.worker.src.tasks.retrieval.index_materials": {"queue": "retrieval"},
    },
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


def autodiscover() -> None:
    __import__("services.worker.src.tasks.ocr")
    __import__("services.worker.src.tasks.retrieval")


autodiscover()


@celery_app.task(name="services.worker.src.health.ping")
def ping() -> str:
    return "pong"
