from __future__ import annotations

from typing import Iterable, List

from ai_edu_core import settings

from services.retrieval.src.documents import DocumentChunk
from services.retrieval.src.vector_store import VectorStore

from .orchestrator import LLMOrchestrator


class RetrievalClient:
    def __init__(
        self,
        *,
        collection_name: str = "learning-materials",
        orchestrator: LLMOrchestrator | None = None,
        vector_store: VectorStore | None = None,
    ) -> None:
        self.orchestrator = orchestrator or LLMOrchestrator()
        self.store = vector_store or VectorStore(collection_name=collection_name)
        self.vector_size = 1536
        self.enabled = self.store.client is not None

    async def search(self, query: str, limit: int = 5) -> List[dict]:
        if settings.enable_mock_ai or not self.enabled:
            return [{"text": f"Mock context for: {query}", "source": "mock"}]
        vector_list = await self.orchestrator.embed(texts=[query])
        vector = vector_list[0]
        results = await self.store.query(vector=vector, limit=limit)
        return results

    async def upsert_documents(self, chunks: Iterable[DocumentChunk]) -> None:
        if not self.enabled:
            return
        await self.store.ensure_collection(vector_size=self.vector_size)
        texts = [chunk.text for chunk in chunks]
        embeddings = await self.orchestrator.embed(texts=texts)
        payloads = [chunk.metadata | {"text": chunk.text, "id": chunk.id} for chunk in chunks]
        await self.store.upsert(embeddings=embeddings, payloads=payloads)
