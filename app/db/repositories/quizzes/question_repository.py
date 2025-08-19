from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.base_repository import BaseRepository
from app.models.quiz_model import Question
from app.schemas.quiz import QuestionSchema
from app.schemas.response_models import ListResponse


class QuestionRepository(BaseRepository[QuestionSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Question)

    async def get_all_questions(
        self, quiz_id: int, limit: int | None = None, offset: int | None = None
    ):
        query = (
            select(Question, func.count().over().label("total_count"))
            .where(Question.quiz_id == quiz_id)
            .offset(offset or 0)
            .limit(limit or 10)
        )

        result = await self.session.execute(query)
        rows = result.all()

        if not rows:
            return ListResponse[QuestionSchema](items=[], count=0)

        total_count = rows[0].total_count

        items = [
            QuestionSchema(id=question.id, text=question.text) for question, _ in rows
        ]

        return ListResponse[QuestionSchema](items=items, count=total_count)
