import logging

from datetime import date
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.exceptions import AppException
from app.core.exceptions.repository_exceptions import RepositoryDatabaseError
from app.db.repositories.base_repository import BaseRepository
from app.models.quiz_model import Records, Question, Quiz, QuizParticipant

logger = logging.getLogger(__name__)


class RecordsRepository(BaseRepository[Records]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Records)

    async def get_average_score_in_company(
        self,
        user_id: int,
        company_id: int,
        from_date: date | None = None,
        to_date: date | None = None,
    ):
        try:
            total_questions_subq = (
                select(
                    Question.quiz_id, func.count(Question.id).label("total_questions")
                )
                .join(Quiz, Quiz.id == Question.quiz_id)
                .where(Quiz.company_id == company_id)
                .group_by(Question.quiz_id)
                .subquery()
            )

            user_scores_subq = (
                select(
                    QuizParticipant.quiz_id,
                    func.sum(Records.score).label("total_score"),
                    func.count(Records.id).label("record_count"),
                    QuizParticipant.completed_at,
                )
                .join(Records, Records.participant_id == QuizParticipant.id)
                .join(Quiz, Quiz.id == QuizParticipant.quiz_id)
                .where(
                    QuizParticipant.user_id == user_id,
                    Quiz.company_id == company_id,
                    *([QuizParticipant.completed_at >= from_date] if from_date else []),
                    *([QuizParticipant.completed_at <= to_date] if to_date else []),
                )
                .group_by(QuizParticipant.quiz_id, QuizParticipant.completed_at)
                .subquery()
            )

            query = select(
                user_scores_subq.c.quiz_id,
                (
                    user_scores_subq.c.total_score
                    / (
                        user_scores_subq.c.record_count
                        * total_questions_subq.c.total_questions
                    )
                    * 100
                ).label("average_score"),
                user_scores_subq.c.completed_at,
            ).join(
                total_questions_subq,
                total_questions_subq.c.quiz_id == user_scores_subq.c.quiz_id,
            )

            result = await self.session.execute(query)
            scores = result.all()

            if not scores:
                return 0, []

            overall_average = sum(row.average_score for row in scores) / len(scores)
            return overall_average, scores

        except SQLAlchemyError as e:
            raise RepositoryDatabaseError(f"Database error: {e}") from e

    async def get_average_score_in_system(
        self, user_id: int, from_date: date | None = None, to_date: date | None = None
    ):
        try:
            total_questions_subq = (
                select(
                    Question.quiz_id, func.count(Question.id).label("total_questions")
                )
                .group_by(Question.quiz_id)
                .subquery()
            )

            user_scores_subq = (
                select(
                    QuizParticipant.quiz_id,
                    QuizParticipant.completed_at,
                    func.sum(Records.score).label("total_score"),
                    func.count(Records.id).label("record_count"),
                )
                .join(Records, Records.participant_id == QuizParticipant.id)
                .where(QuizParticipant.user_id == user_id)
            )

            if from_date:
                user_scores_subq = user_scores_subq.where(
                    QuizParticipant.completed_at >= from_date
                )
            if to_date:
                user_scores_subq = user_scores_subq.where(
                    QuizParticipant.completed_at <= to_date
                )

            user_scores_subq = user_scores_subq.group_by(
                QuizParticipant.quiz_id, QuizParticipant.completed_at
            ).subquery()

            query = (
                select(
                    Quiz.title,
                    Quiz.description,
                    user_scores_subq.c.completed_at,
                    (
                        user_scores_subq.c.total_score
                        / (
                            user_scores_subq.c.record_count
                            * total_questions_subq.c.total_questions
                        )
                        * 100
                    ).label("average_score"),
                )
                .join(user_scores_subq, user_scores_subq.c.quiz_id == Quiz.id)
                .join(total_questions_subq, total_questions_subq.c.quiz_id == Quiz.id)
            )

            result = await self.session.execute(query)
            scores = result.all()

            if not scores:
                return 0, []

            overall_average = sum(row.average_score for row in scores) / len(scores)
            return overall_average, scores

        except SQLAlchemyError as e:
            raise RepositoryDatabaseError(f"Database error: {e}") from e
