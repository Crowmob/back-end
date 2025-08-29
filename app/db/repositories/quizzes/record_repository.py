from datetime import date

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.base_repository import BaseRepository
from app.models.quiz_model import Records, Question, Quiz, QuizParticipant


class RecordsRepository(BaseRepository[Records]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Records)

    async def get_average_score_in_company(
        self, company_id: int, from_date: date, to_date: date
    ):
        total_questions_subquery = (
            select(Question.quiz_id, func.count(Question.id).label("total_questions"))
            .join(Quiz, Quiz.id == Question.quiz_id)
            .where(Quiz.company_id == company_id)
            .group_by(Question.quiz_id)
            .subquery()
        )

        user_score_subquery = (
            select(
                QuizParticipant.quiz_id,
                QuizParticipant.user_id,
                func.coalesce(func.sum(Records.score), 0).label("user_score"),
                QuizParticipant.completed_at,
            )
            .join(Records, Records.participant_id == QuizParticipant.id)
            .join(Quiz, Quiz.id == QuizParticipant.quiz_id)
            .where(
                Quiz.company_id == company_id,
                QuizParticipant.completed_at >= from_date,
                QuizParticipant.completed_at <= to_date,
            )
            .group_by(
                QuizParticipant.quiz_id,
                QuizParticipant.completed_at,
                QuizParticipant.user_id,
            )
            .subquery()
        )

        query = select(
            user_score_subquery.c.quiz_id,
            user_score_subquery.c.user_id,
            (
                user_score_subquery.c.user_score
                * 100
                / total_questions_subquery.c.total_questions
            ).label("average_score"),
            user_score_subquery.c.completed_at,
        ).join(
            total_questions_subquery,
            total_questions_subquery.c.quiz_id == user_score_subquery.c.quiz_id,
        )

        result = await self.session.execute(query)
        scores = result.all()

        if not scores:
            return [0, []]

        overall_average = sum(avg for _, _, avg, _ in scores) / len(scores)
        return [overall_average, scores]

    async def get_average_score_in_system(
        self, user_id: int, from_date: date | None, to_date: date | None
    ):
        total_questions_subquery = (
            select(Question.quiz_id, func.count(Question.id).label("total_questions"))
            .group_by(Question.quiz_id)
            .subquery()
        )

        user_score_query = (
            select(
                QuizParticipant.quiz_id,
                func.coalesce(func.sum(Records.score), 0).label("user_score"),
                QuizParticipant.completed_at,
            )
            .join(Records, Records.participant_id == QuizParticipant.id)
            .where(QuizParticipant.user_id == user_id)
        )

        if from_date:
            user_score_query = user_score_query.where(
                QuizParticipant.completed_at >= from_date
            )
        if to_date:
            user_score_query = user_score_query.where(
                QuizParticipant.completed_at <= to_date
            )

        user_score_subquery = user_score_query.group_by(
            QuizParticipant.quiz_id, QuizParticipant.completed_at
        ).subquery()

        query = select(
            user_score_subquery.c.quiz_id,
            (
                user_score_subquery.c.user_score
                * 100
                / total_questions_subquery.c.total_questions
            ).label("average_score"),
            user_score_subquery.c.completed_at,
        ).join(
            total_questions_subquery,
            total_questions_subquery.c.quiz_id == user_score_subquery.c.quiz_id,
        )

        result = await self.session.execute(query)
        scores = result.all()

        if not scores:
            return [0, []]

        overall_average = sum(avg for _, avg, _ in scores) / len(scores)
        return [overall_average, scores]
