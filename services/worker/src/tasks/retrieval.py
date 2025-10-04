from __future__ import annotations

from pathlib import Path
from typing import Iterable

from services.ai.src.orchestrator import LLMOrchestrator
from services.ai.src.retrieval_client import RetrievalClient
from services.retrieval.src.documents import DocumentChunk, load_text_documents

from ..celery_app import celery_app


def _load_documents(paths: Iterable[str]) -> list[DocumentChunk]:
    path_objs = [Path(p) for p in paths]
    return list(load_text_documents(path_objs))


@celery_app.task(name="services.worker.src.tasks.retrieval.index_materials")
def index_materials(paths: list[str]) -> dict:
    orchestrator = LLMOrchestrator()
    retriever = RetrievalClient(orchestrator=orchestrator)
    chunks = _load_documents(paths)
    if not chunks:
        return {"status": "no_documents"}
    import asyncio

    asyncio.run(retriever.upsert_documents(chunks))
    return {"status": "indexed", "documents": len(chunks)}
