from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres_init import async_session_maker
from app.db.repositories.membership_requests_repository import (
    MembershipRequestsRepository,
)
from app.db.repositories.quizzes.answer_repository import AnswerRepository
from app.db.repositories.quizzes.participant_repository import QuizParticipantRepository
from app.db.repositories.quizzes.question_repository import QuestionRepository
from app.db.repositories.quizzes.quiz_repository import QuizRepository
from app.db.repositories.quizzes.record_repository import RecordsRepository
from app.db.repositories.user_repository import UserRepository
from app.db.repositories.company_repository import CompanyRepository
from app.db.repositories.membership_repository import MembershipRepository


class UnitOfWork:
    def __init__(self, session: AsyncSession | None = None):
        self._external_session = session
        self.session = None
        self.users = None
        self.companies = None
        self.memberships = None
        self.membership_requests = None
        self.quizzes = None
        self.questions = None
        self.answers = None
        self.participants = None
        self.records = None

    async def __aenter__(self):
        if self._external_session:
            self.session = self._external_session
        else:
            self._session_context = async_session_maker()
            self.session = await self._session_context.__aenter__()

        self.users = UserRepository(self.session)
        self.companies = CompanyRepository(self.session)
        self.memberships = MembershipRepository(self.session)
        self.membership_requests = MembershipRequestsRepository(self.session)
        self.quizzes = QuizRepository(self.session)
        self.questions = QuestionRepository(self.session)
        self.answers = AnswerRepository(self.session)
        self.participants = QuizParticipantRepository(self.session)
        self.records = RecordsRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.session.rollback()
        else:
            await self.session.commit()

        if not self._external_session:
            await self._session_context.__aexit__(exc_type, exc_val, exc_tb)

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
