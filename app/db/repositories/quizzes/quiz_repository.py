import logging

from sqlalchemy import select, func, and_, Integer, cast, case, text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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

    async def get_all_quizzes(
        self,
        user_id: int,
        company_id: int | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ):
        last_completion_all_subq = (
            select(
                QuizParticipant.quiz_id,
                func.max(QuizParticipant.completed_at).label("last_completed_at"),
            )
            .group_by(QuizParticipant.quiz_id)
            .subquery()
        )

        last_completion_user_subq = (
            select(
                QuizParticipant.quiz_id,
                func.max(QuizParticipant.completed_at).label("user_last_completed"),
            )
            .where(QuizParticipant.user_id == user_id)
            .group_by(QuizParticipant.quiz_id)
            .subquery()
        )

        extra_columns = [
            last_completion_all_subq.c.last_completed_at,
            case(
                (
                    last_completion_user_subq.c.user_last_completed != None,
                    func.now()
                    >= last_completion_user_subq.c.user_last_completed
                    + cast(Quiz.frequency, Integer) * text("INTERVAL '1 day'"),
                ),
                else_=True,
            ).label("is_available"),
        ]

        filters = {"company_id": company_id} if company_id is not None else None

        items, total_count = await self.get_all(
            filters=filters,
            limit=limit or 5,
            offset=offset or 0,
            extra_columns=extra_columns,
            outer_joins=[
                (
                    last_completion_all_subq,
                    last_completion_all_subq.c.quiz_id == Quiz.id,
                ),
                (
                    last_completion_user_subq,
                    last_completion_user_subq.c.quiz_id == Quiz.id,
                ),
            ],
        )
        return items, total_count

    async def get_full_quiz_data_for_user(self, selected_answer_ids: list[int]):
        try:
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
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError: {e}")
            raise AppException(detail="Database exception occurred.")
