from __future__ import annotations

from typing import Iterable, List

from ai_edu_core import settings

try:
    from qdrant_client import AsyncQdrantClient
    from qdrant_client.http import models as rest
except ImportError:  # pragma: no cover - optional dependency
    AsyncQdrantClient = None  # type: ignore
    rest = None  # type: ignore


class VectorStore:
    def __init__(self, collection_name: str = "learning-materials") -> None:
        if AsyncQdrantClient is None:
            self.client = None
            self.collection_name = collection_name
            return
        self.collection_name = collection_name
        self.client = AsyncQdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)

    async def ensure_collection(self, vector_size: int, distance: str = "Cosine") -> None:
        if self.client is None or rest is None:
            return
        collections = await self.client.get_collections()
        if not any(c.name == self.collection_name for c in collections.collections):
            dist_enum = getattr(rest.Distance, distance.upper(), rest.Distance.COSINE)
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=rest.VectorParams(size=vector_size, distance=dist_enum),
            )

    async def upsert(
        self,
        embeddings: List[List[float]],
        payloads: Iterable[dict],
    ) -> None:
        if self.client is None or rest is None:
            return
        payload_list = list(payloads)
        ids = [payload.get("id") for payload in payload_list]
        ids = [str(idx) if idx is not None else str(i) for i, idx in enumerate(ids)]
        await self.client.upsert(
            collection_name=self.collection_name,
            wait=True,
            points=rest.Batch(vectors=embeddings, payloads=payload_list, ids=ids),
        )

    async def query(self, vector: List[float], limit: int = 5) -> list[dict]:
        if self.client is None or rest is None:
            return []
        response = await self.client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            with_payload=True,
            limit=limit,
        )
        return [hit.payload | {"score": hit.score} for hit in response]
