import pytest, pytest_asyncio

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from fastapi import HTTPException

from app.schemas.user import UserSchema, UserUpdateRequestModel, GetAllUsersRequestModel
from app.services.user import UserServices
from app.db.unit_of_work import UnitOfWork
from app.core.settings_model import settings


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(settings.db.URL, echo=False)
    test_session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with test_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
def user_services(session, monkeypatch):
    def unit_of_work_with_session():
        return UnitOfWork(session=session)

    monkeypatch.setattr("app.services.user.UnitOfWork", unit_of_work_with_session)
    return UserServices()


@pytest.mark.asyncio
async def test_create_user(user_services):
    user_data = UserSchema(
        username="testname1",
        email="test1@mail.com",
        password="1234",
        date_of_birth="2000-01-01",
        gender="male",
    )
    global user_id
    user_id = await user_services.create_user(user_data)
    assert type(user_id) == int


@pytest.mark.asyncio
async def test_get_all_users(user_services):
    data = GetAllUsersRequestModel(limit=1)
    users_list = await user_services.get_all_users(data)
    assert len(users_list.items) == 1


@pytest.mark.asyncio
async def test_get_user_by_id(user_services):
    user = await user_services.get_user_by_id(user_id)
    assert user.username == "testname1"


@pytest.mark.asyncio
async def test_update_user(user_services):
    await user_services.update_user(
        user_id, UserUpdateRequestModel(username="testname2")
    )
    user = await user_services.get_user_by_id(user_id)
    assert user.username == "testname2"


@pytest.mark.asyncio
async def test_delete_user(user_services):
    await user_services.delete_user(user_id)
    with pytest.raises(HTTPException) as exc_info:
        await user_services.get_user_by_id(user_id)

    assert exc_info.value.status_code == 404
