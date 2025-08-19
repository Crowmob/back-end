from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.base_repository import BaseRepository
from app.models.quiz_model import QuizParticipant, Quiz
from app.schemas.quiz import QuizSchema
from app.schemas.response_models import ListResponse


class QuizRepository(BaseRepository[QuizSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Quiz)

    async def create_quiz_participant(self, quiz_id: int, user_id: int, score: int):
        quiz_participant = QuizParticipant(quiz_id, user_id, score)
        self.session.add(quiz_participant)

    async def get_all_quizzes(
        self, company_id: int, limit: int | None = None, offset: int | None = None
    ):
        query = (
            select(Quiz, func.count().over().label("total_count"))
            .where(Quiz.company_id == company_id)
            .offset(offset or 0)
            .limit(limit or 10)
        )

        result = await self.session.execute(query)
        rows = result.all()

        if not rows:
            return ListResponse[QuizSchema](items=[], count=0)

        total_count = rows[0].total_count

        items = [
            QuizSchema(
                id=quiz.id,
                title=quiz.title,
                description=quiz.description,
            )
            for quiz, _ in rows
        ]

        return ListResponse[QuizSchema](items=items, count=total_count)
