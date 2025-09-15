import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, DataError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.exceptions import AppException, BadRequestException
from app.core.exceptions.repository_exceptions import (
    RepositoryIntegrityError,
    RepositoryDataError,
    RepositoryDatabaseError,
)
from app.db.repositories.base_repository import BaseRepository
from app.models.quiz_model import (
    Answer,
    SelectedAnswers,
    QuizParticipant,
    Records,
    Quiz,
)

logger = logging.getLogger(__name__)


class AnswerRepository(BaseRepository[Answer]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Answer)

    async def create_selected_answers(self, selected_answers: list[SelectedAnswers]):
        try:
            self.session.add_all(selected_answers)
            await self.session.flush()
            ids = [answer.id for answer in selected_answers]
            return ids
        except IntegrityError as e:
            raise RepositoryIntegrityError(f"Integrity error: {e}") from e
        except DataError as e:
            raise RepositoryDataError(f"Invalid data: {e}") from e
        except SQLAlchemyError as e:
            raise RepositoryDatabaseError(f"Database error: {e}") from e

    async def get_missing_answers(
        self,
        answer_ids: list[int],
        user_id: int,
        quiz_id: int = None,
        company_id: int = None,
    ):
        try:
            query = (
                select(SelectedAnswers)
                .join(Records, SelectedAnswers.record_id == Records.id)
                .join(QuizParticipant, Records.participant_id == QuizParticipant.id)
                .join(Quiz, QuizParticipant.quiz_id == Quiz.id)
                .filter(QuizParticipant.user_id == user_id)
            )

            if quiz_id:
                query = query.filter(QuizParticipant.quiz_id == quiz_id)

            if company_id:
                query = query.filter(Quiz.company_id == company_id)

            if answer_ids:
                query = query.filter(~SelectedAnswers.id.in_(answer_ids))

            result = await self.session.execute(query)
            rows = result.scalars().all()
            return rows
        except SQLAlchemyError as e:
            raise RepositoryDatabaseError(f"Database error: {e}") from e
