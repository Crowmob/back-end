from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.base_repository import BaseRepository
from app.models.quiz_model import Records, Question, Quiz, QuizParticipant


class RecordsRepository(BaseRepository[Records]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Records)

    async def get_average_score_in_company(self, user_id: int, company_id: int):
        total_questions_q = (
            select(func.count(Question.id))
            .join(Quiz, Quiz.id == Question.quiz_id)
            .where(Quiz.company_id == company_id)
        ).scalar_subquery()

        user_correct_q = (
            select(func.coalesce(func.sum(Records.score), 0))
            .join(QuizParticipant, QuizParticipant.id == Records.participant_id)
            .join(Quiz, Quiz.id == QuizParticipant.quiz_id)
            .where(
                QuizParticipant.user_id == user_id,
                Quiz.company_id == company_id,
            )
        ).scalar_subquery()

        query = select(
            (user_correct_q * 100 / func.nullif(total_questions_q, 0)).label(
                "percentage"
            )
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none() or 0
