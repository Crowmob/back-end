from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.base_repository import BaseRepository
from app.models.quiz_model import QuizParticipant, Quiz
from app.schemas.quiz import QuizSchema, QuizDetailResponse
from app.schemas.response_models import ListResponse


class QuizRepository(BaseRepository[Quiz]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Quiz)

    async def create_quiz_participant(self, quiz_id: int, user_id: int, score: int):
        quiz_participant = QuizParticipant(quiz_id, user_id, score)
        self.session.add(quiz_participant)

    async def get_all_quizzes(
        self, company_id: int, limit: int | None = None, offset: int | None = None
    ):
        items, total_count = await super().get_all(
            filters={"company_id": company_id},
            limit=limit,
            offset=offset,
        )

        return ListResponse[QuizDetailResponse](
            items=[
                QuizDetailResponse(
                    id=quiz.id, title=quiz.title, description=quiz.description
                )
                for quiz in items
            ],
            count=total_count,
        )
