import pytest

from sqlalchemy import insert, select

from app.schemas.user import UserSchema, UserUpdateRequestModel, GetAllUsersRequestModel
from app.models.user_model import User


@pytest.mark.asyncio
async def test_create_user(db_session, user_services_fixture):
    user_data = UserSchema(username="test", email="test@example.com", password="1234")

    user_id = await user_services_fixture.create_user(
        user_data.username, user_data.email, user_data.password
    )
    assert isinstance(user_id, int)

    db_user = await db_session.scalar(select(User).where(User.id == user_id))
    assert db_user.username == user_data.username
    assert db_user.email == user_data.email


@pytest.mark.asyncio
async def test_get_all_users(db_session, user_services_fixture):
    await db_session.execute(
        insert(User).values(
            username="test1", email="test1@example.com", password="1234"
        )
    )
    await db_session.execute(
        insert(User).values(
            username="test2", email="test2@example.com", password="1234"
        )
    )
    await db_session.commit()

    data = GetAllUsersRequestModel(limit=2)
    users_list = await user_services_fixture.get_all_users(data.limit, data.offset)
    assert len(users_list.items) == 2


@pytest.mark.asyncio
async def test_get_user_by_id(user_services_fixture, test_user):
    user = await user_services_fixture.get_user_by_id(
        test_user["id"], test_user["email"]
    )

    assert user.username == "test"
    assert user.email == "test@example.com"


@pytest.mark.asyncio
async def test_get_user_by_email(user_services_fixture, test_user):
    user = await user_services_fixture.get_user_by_email(test_user["email"])

    assert user.username == "test"
    assert user.email == "test@example.com"


@pytest.mark.asyncio
async def test_update_user(db_session, user_services_fixture, test_user):
    data = UserUpdateRequestModel(username="updated")
    await user_services_fixture.update_user(
        test_user["id"], data.username, data.password
    )

    updated_user = await db_session.scalar(
        select(User).where(User.id == test_user["id"])
    )
    assert updated_user.username == "updated"


@pytest.mark.asyncio
async def test_delete_user(db_session, user_services_fixture, test_user):
    await user_services_fixture.delete_user(test_user["id"])

    user = await db_session.scalar(select(User).where(User.id == test_user["id"]))
    assert user.has_profile is False
