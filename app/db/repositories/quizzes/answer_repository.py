from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.base_repository import BaseRepository
from app.models.quiz_model import Answer
from app.schemas.quiz import AnswerDetailResponse


class AnswerRepository(BaseRepository[Answer]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Answer)

    async def get_all_answers(self, question_id: int):
        result = await self.session.execute(
            select(Answer).where(Answer.question_id == question_id)
        )
        rows = result.scalars().all()

        return [AnswerDetailResponse.model_validate(row) for row in rows]
