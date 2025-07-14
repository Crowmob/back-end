import pytest

from fastapi.testclient import TestClient

from app.main import app
from app.db.redis_init import get_redis_client
from app.schemas.user import UserSchema, UserUpdateRequestModel

client = TestClient(app)


def test_health_check():
    response = client.get("/")
    assert response.json() == {"status_code": 200, "detail": "ok", "result": "working"}
