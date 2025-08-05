import pytest
import pytest_asyncio

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import insert

from app.services.user import user_services
from app.db.unit_of_work import UnitOfWork
from app.utils.settings_model import settings
from app.models.user_model import User
from app.utils.db import truncate_users_table


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(settings.db.get_url(settings.ENV), echo=False)
    test_session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with test_session_maker() as session:
        await truncate_users_table(session)
        yield session
        await session.rollback()


@pytest.fixture
def user_services_fixture(db_session, monkeypatch):
    def unit_of_work_with_session():
        return UnitOfWork(session=db_session)

    monkeypatch.setattr("app.services.user.UnitOfWork", unit_of_work_with_session)
    return user_services


@pytest.fixture
def company_services_fixture(db_session, monkeypatch):
    def unit_of_work_with_session():
        return UnitOfWork(session=db_session)

    monkeypatch.setattr("app.services.company.UnitOfWork", unit_of_work_with_session)
    return company_services


@pytest_asyncio.fixture
async def test_user(db_session):
    result = await db_session.execute(
        insert(User)
        .values(username="test", email="test@example.com", password="1234")
        .returning(User.id, User.email)
    )
    user_id, email = result.one()
    await db_session.commit()
    return {"id": user_id, "email": email}
