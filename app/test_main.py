from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.db.redis_init import get_redis_client
from app.schemas.user import UserSchema, UserUpdateRequestModel
from app.services.user import (
    createUser,
    getAllUsers,
    getUserById,
    updateUser,
    deleteUser,
)

client = TestClient(app)


def test_health_check():
    response = client.get("/")
    assert response.json() == {"status_code": 200, "detail": "ok", "result": "working"}


@pytest.mark.asyncio
async def test_redis():
    await get_redis_client().set("id:1", "hello", ex=(30))
    data = await get_redis_client().get("id:1")
    decoded_data = data.decode()
    assert decoded_data == "hello"


@pytest.mark.asyncio
async def test_crud_operations():
    user_data = UserSchema(
        username="testname1",
        email="test1@mail.com",
        password="1234",
        date_of_birth="2000-01-01",
        gender="male",
    )
    user_id = await createUser(user_data)
    users = await getAllUsers()
    assert len(users) > 0

    fetched_user_data = await getUserById(user_id)
    assert user_data == fetched_user_data

    await updateUser(user_id, UserUpdateRequestModel(username="testname2"))
    fetched_user_data = await getUserById(user_id)
    assert fetched_user_data.username == "testname2"

    await deleteUser(user_id)
    users = await getAllUsers()
    assert len(users) == 0
