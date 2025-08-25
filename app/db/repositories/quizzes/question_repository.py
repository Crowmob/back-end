from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.base_repository import BaseRepository
from app.models.quiz_model import Question
from app.schemas.quiz import QuestionDetailResponse
from app.schemas.response_models import ListResponse


class QuestionRepository(BaseRepository[Question]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Question)

    async def get_all_questions(
        self, quiz_id: int, limit: int | None = None, offset: int | None = None
    ):
        items, total_count = await super().get_all(
            filters={"quiz_id": quiz_id},
            limit=limit,
            offset=offset,
        )

        return ListResponse[QuestionDetailResponse](
            items=[
                QuestionDetailResponse(
                    id=question.id,
                    text=question.text,
                )
                for question in items
            ],
            count=total_count,
        )
