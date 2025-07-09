from fastapi.testclient import TestClient
from sqlalchemy import text
import pytest

from app.main import app
from app.db.postgres_init import async_session_maker
from app.db.redis_init import get_redis_client

client = TestClient(app)


def test_health_check():
    response = client.get("/")
    assert response.json() == {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }


@pytest.mark.asyncio
async def test_postgres():
    async with async_session_maker() as session:
        data = await session.execute(text("SELECT id, name FROM users"))
        rows = data.fetchall()
        assert rows == [(1, "hello")]


@pytest.mark.asyncio
async def test_redis():
    data = await get_redis_client().get("id:1")
    decoded_data = data.decode()
    assert decoded_data == "hello"
