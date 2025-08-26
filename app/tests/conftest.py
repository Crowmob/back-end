import fakeredis
import pytest
import pytest_asyncio

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import insert

from app.models.company_model import Company
from app.models.quiz_model import Answer, Question, Quiz, QuizParticipant, Records
from app.services.quiz import quiz_services
from app.services.user import user_services
from app.services.company import company_services
from app.db.unit_of_work import UnitOfWork
from app.utils.settings_model import settings
from app.models.user_model import User
from app.models.membership_model import Memberships, MembershipRequests, RoleEnum
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


@pytest_asyncio.fixture
async def redis_client():
    client = await fakeredis.aioredis.FakeRedis()
    yield client
    await client.close()


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


@pytest.fixture
def quiz_services_fixture(db_session, redis_client, monkeypatch):
    def unit_of_work_with_session():
        return UnitOfWork(session=db_session)

    monkeypatch.setattr("app.services.quiz.UnitOfWork", unit_of_work_with_session)
    monkeypatch.setattr("app.services.quiz.get_redis_client", lambda: redis_client)
    return quiz_services


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
        .values(owner=test_user["id"], name="test", description="test", private=False)
        .returning(Company.id)
    )
    company_id = result.one()[0]
    await db_session.commit()
    return {"id": company_id, "owner": test_user["id"]}


@pytest_asyncio.fixture
async def test_membership_request(db_session, test_user, test_company):
    result = await db_session.execute(
        insert(MembershipRequests)
        .values(type="request", user_id=test_user["id"], company_id=test_company["id"])
        .returning(MembershipRequests.id)
    )
    membership_request_id = result.one()[0]
    await db_session.commit()
    return {
        "id": membership_request_id,
        "user_id": test_user["id"],
        "company_id": test_company["id"],
    }


@pytest_asyncio.fixture
async def test_membership(db_session, test_user, test_company):
    result = await db_session.execute(
        insert(Memberships)
        .values(user_id=test_user["id"], company_id=test_company["id"])
        .returning(Memberships.id)
    )
    membership_id = result.one()[0]
    await db_session.commit()
    return {
        "id": membership_id,
        "user_id": test_user["id"],
        "company_id": test_company["id"],
        "owner": test_company["owner"],
    }


@pytest_asyncio.fixture
async def test_admin(db_session, test_company):
    result = await db_session.execute(
        insert(Memberships)
        .values(
            role=RoleEnum.ADMIN.value,
            user_id=test_company["owner"],
            company_id=test_company["id"],
        )
        .returning(Memberships.id)
    )
    membership_id = result.one()[0]
    await db_session.commit()
    return {
        "id": membership_id,
        "user_id": test_company["owner"],
        "company_id": test_company["id"],
    }


@pytest_asyncio.fixture
async def test_answers(db_session, test_questions):
    res = {}
    for i in range(2):
        result = await db_session.execute(
            insert(Answer)
            .values(
                text="Test answer",
                is_correct=True,
                question_id=test_questions["id1" if i == 0 else "id2"],
            )
            .returning(Answer.id)
        )
        answer_id1 = result.one()[0]
        result = await db_session.execute(
            insert(Answer)
            .values(
                text="Test answer",
                is_correct=False,
                question_id=test_questions["id1" if i == 0 else "id2"],
            )
            .returning(Answer.id)
        )
        answer_id2 = result.one()[0]
        res[f"id{i * 2 + 1}"] = answer_id1
        res[f"id{i * 2 + 2}"] = answer_id2
    res["question_id1"] = test_questions["id1"]
    res["question_id2"] = test_questions["id2"]
    return res


@pytest_asyncio.fixture
async def test_questions(db_session, test_quiz):
    result = await db_session.execute(
        insert(Question)
        .values(text="Test question", quiz_id=test_quiz["id"])
        .returning(Question.id)
    )
    question_id1 = result.one()[0]
    result = await db_session.execute(
        insert(Question)
        .values(text="Test question", quiz_id=test_quiz["id"])
        .returning(Question.id)
    )
    question_id2 = result.one()[0]
    return {"quiz_id": test_quiz["id"], "id1": question_id1, "id2": question_id2}


@pytest_asyncio.fixture
async def test_quiz(db_session, test_company):
    result = await db_session.execute(
        insert(Quiz)
        .values(
            title="Test quiz",
            description="Test quiz",
            company_id=test_company["id"],
        )
        .returning(Quiz.id)
    )
    quiz_id = result.one()[0]
    return {"id": quiz_id, "company_id": test_company["id"]}


@pytest_asyncio.fixture
async def test_participant(db_session, test_quiz, test_user):
    result = await db_session.execute(
        insert(QuizParticipant)
        .values(
            user_id=test_user["id"],
            quiz_id=test_quiz["id"],
        )
        .returning(QuizParticipant.id)
    )
    participant_id = result.one()[0]
    return {"id": participant_id, "quiz_id": test_quiz["id"]}


@pytest_asyncio.fixture
async def test_record(db_session, test_participant):
    result = await db_session.execute(
        insert(Records)
        .values(participant_id=test_participant["id"], score=1)
        .returning(Records.id)
    )
    record_id = result.one()[0]
    return {"id": record_id, "participant_id": test_participant["id"]}
