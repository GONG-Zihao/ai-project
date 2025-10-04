import os
from typing import Any, Dict

import httpx

API_BASE_URL = os.getenv("API_BASE_URL")


class StreamlitAPIClient:
    def __init__(self) -> None:
        self.base_url = API_BASE_URL.rstrip("/") if API_BASE_URL else None
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0) if self.base_url else None

    def is_enabled(self) -> bool:
        return self._client is not None

    async def login(self, tenant: str, username: str, password: str) -> Dict[str, Any]:
        if not self._client:
            raise RuntimeError("API client disabled")
        response = await self._client.post(
            "/auth/login",
            json={"tenant_slug": tenant, "username": username, "password": password},
        )
        response.raise_for_status()
        return response.json()

    async def ask_question(self, token: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self._client:
            raise RuntimeError("API client disabled")
        headers = {"Authorization": f"Bearer {token}"}
        response = await self._client.post("/qa/ask", json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

    async def get_mistakes(self, token: str) -> Dict[str, Any]:
        if not self._client:
            raise RuntimeError("API client disabled")
        headers = {"Authorization": f"Bearer {token}"}
        response = await self._client.get("/mistakes", headers=headers)
        response.raise_for_status()
        return {"items": response.json()}

    async def create_mistake(self, token: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self._client:
            raise RuntimeError("API client disabled")
        headers = {"Authorization": f"Bearer {token}"}
        response = await self._client.post("/mistakes", json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

    async def get_learning_plan(self, token: str) -> Dict[str, Any]:
        if not self._client:
            raise RuntimeError("API client disabled")
        headers = {"Authorization": f"Bearer {token}"}
        response = await self._client.get("/learning/plan", headers=headers)
        response.raise_for_status()
        return response.json()

    async def get_knowledge_mastery(self, token: str, subject: str | None = None) -> Dict[str, Any]:
        if not self._client:
            raise RuntimeError("API client disabled")
        headers = {"Authorization": f"Bearer {token}"}
        params = {"subject": subject} if subject else None
        response = await self._client.get("/learning/knowledge", headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    async def get_learning_overview(self, token: str) -> Dict[str, Any]:
        if not self._client:
            raise RuntimeError("API client disabled")
        headers = {"Authorization": f"Bearer {token}"}
        response = await self._client.get("/learning/overview", headers=headers)
        response.raise_for_status()
        return response.json()

    async def get_progress_metrics(self, token: str) -> Dict[str, Any]:
        if not self._client:
            raise RuntimeError("API client disabled")
        headers = {"Authorization": f"Bearer {token}"}
        response = await self._client.get("/analytics/progress", headers=headers)
        response.raise_for_status()
        return response.json()

    async def get_achievements(self, token: str) -> Dict[str, Any]:
        if not self._client:
            raise RuntimeError("API client disabled")
        headers = {"Authorization": f"Bearer {token}"}
        response = await self._client.get("/analytics/achievements", headers=headers)
        response.raise_for_status()
        return response.json()


api_client = StreamlitAPIClient()
