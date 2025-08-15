import pytest
import pytest_asyncio

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import insert

from app.models.company_model import Company
from app.services.user import user_services
from app.services.company import company_services
from app.db.unit_of_work import UnitOfWork
from app.utils.settings_model import settings
from app.models.user_model import User
from app.models.membership_model import Memberships, MembershipRequests
from app.services.admin import admin_services
from app.services.membership import membership_services
from app.utils.db import clear_tables


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(settings.db.get_url(settings.ENV), echo=False)
    test_session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with test_session_maker() as session:
        await clear_tables(session)
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


@pytest.fixture
def membership_services_fixture(db_session, monkeypatch):
    def unit_of_work_with_session():
        return UnitOfWork(session=db_session)

    monkeypatch.setattr("app.services.membership.UnitOfWork", unit_of_work_with_session)
    return membership_services


@pytest.fixture
def admin_services_fixture(db_session, monkeypatch):
    def unit_of_work_with_session():
        return UnitOfWork(session=db_session)

    monkeypatch.setattr("app.services.admin.UnitOfWork", unit_of_work_with_session)
    return admin_services


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


@pytest_asyncio.fixture
async def test_company(db_session, test_user):
    result = await db_session.execute(
        insert(Company)
        .values(owner=test_user["id"], name="test", description="test", private=True)
        .returning(Company.id)
    )
    company_id = result.one()[0]
    await db_session.commit()
    return company_id


@pytest_asyncio.fixture
async def test_membership_request(db_session, test_user, test_company):
    result = await db_session.execute(
        insert(MembershipRequests)
        .values(type="request", from_id=test_user["id"], to_id=test_company)
        .returning(MembershipRequests.id)
    )
    membership_request_id = result.one()[0]
    await db_session.commit()
    return {
        "id": membership_request_id,
        "user_id": test_user["id"],
        "company_id": test_company,
    }


@pytest_asyncio.fixture
async def test_membership(db_session, test_user, test_company):
    result = await db_session.execute(
        insert(Memberships)
        .values(user_id=test_user["id"], company_id=test_company)
        .returning(Memberships.id)
    )
    membership_id = result.one()[0]
    await db_session.commit()
    return {"id": membership_id, "user_id": test_user["id"], "company_id": test_company}


@pytest_asyncio.fixture
async def test_admin(db_session, test_user, test_company):
    result = await db_session.execute(
        insert(Memberships)
        .values(role="admin", user_id=test_user["id"], company_id=test_company)
        .returning(Memberships.id)
    )
    membership_id = result.one()[0]
    await db_session.commit()
    return {"id": membership_id, "user_id": test_user["id"], "company_id": test_company}
