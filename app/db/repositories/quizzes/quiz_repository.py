import logging

from sqlalchemy import select, func, and_, Integer, cast, case, text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, aliased

from app.core.exceptions.exceptions import AppException, BadRequestException
from app.db.repositories.base_repository import BaseRepository
from app.models.quiz_model import (
    QuizParticipant,
    Quiz,
    Records,
    Question,
    Answer,
    SelectedAnswers,
)

logger = logging.getLogger(__name__)


class QuizRepository(BaseRepository[Quiz]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Quiz)

    async def create_quiz_participant(self, quiz_id: int, user_id: int, score: int):
        try:
            quiz_participant = QuizParticipant(quiz_id=quiz_id, user_id=user_id)
            self.session.add(quiz_participant)
            await self.session.flush()
            await self.session.refresh(quiz_participant)
            record = Records(participant_id=quiz_participant.id, score=score)
            self.session.add(record)
        except IntegrityError as e:
            logger.error(f"IntegrityError: {e}")
            raise BadRequestException(detail="Failed to update. Wrong data")
        except DataError as e:
            logger.error(f"Data error: {e}")
            raise BadRequestException(detail="Invalid format or length of fields")
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError: {e}")
            raise AppException(detail="Database exception occurred.")

    async def get_quiz_by_id(self, quiz_id: int, company_id: int):
        try:
            stmt = (
                select(Quiz)
                .where(Quiz.id == quiz_id, Quiz.company_id == company_id)
                .options(selectinload(Quiz.questions).selectinload(Question.answers))
            )
            result = await self.session.execute(stmt)
            quiz = result.scalar_one_or_none()

            if quiz is None:
                return None

            return quiz
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError: {e}")
            raise AppException(detail="Database exception occurred.")

    async def get_all_quizzes(
        self,
        company_id: int,
        user_id: int,
        limit: int | None = None,
        offset: int | None = None,
    ):
        try:
            is_available_case = case(
                (
                    QuizParticipant.completed_at != None,
                    func.now()
                    >= QuizParticipant.completed_at
                    + cast(Quiz.frequency, Integer) * text("INTERVAL '1 day'"),
                ),
                else_=True,
            ).label("is_available")

            items, total_count = await super().get_all(
                limit=limit,
                offset=offset,
                outer_joins=[
                    (
                        QuizParticipant,
                        and_(
                            QuizParticipant.quiz_id == Quiz.id,
                            QuizParticipant.user_id == user_id,
                        ),
                    )
                ],
                extra_filters=[Quiz.company_id == company_id],
                extra_columns=[
                    Quiz.id,
                    Quiz.title,
                    Quiz.description,
                    Quiz.frequency,
                    QuizParticipant.completed_at,
                    is_available_case,
                ],
            )

            return items, total_count
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError: {e}")
            raise AppException(detail="Database exception occurred.")

    async def get_full_quiz_data_for_user(self, selected_answer_ids: list[int]):
        query = (
            select(
                Answer.text.label("answer_text"),
                Answer.is_correct,
                Question.text.label("question_text"),
                Quiz.title.label("quiz_title"),
                Quiz.description.label("quiz_description"),
            )
            .select_from(SelectedAnswers)
            .join(Answer, SelectedAnswers.answer_id == Answer.id)
            .join(Question, Answer.question_id == Question.id)
            .join(Quiz, Question.quiz_id == Quiz.id)
            .filter(SelectedAnswers.id.in_(selected_answer_ids))
        )

        result = await self.session.execute(query)
        rows = result.fetchall()

        return rows
