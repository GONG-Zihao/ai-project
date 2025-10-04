import pytest
from httpx import AsyncClient

from services.api.src.main import app


@pytest.mark.asyncio
async def test_healthcheck():
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
