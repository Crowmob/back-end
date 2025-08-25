from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.base_repository import BaseRepository
from app.models.quiz_model import QuizParticipant
from app.schemas.quiz import QuizParticipantDetailResponse


class QuizParticipantRepository(BaseRepository[QuizParticipant]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, QuizParticipant)

    async def get_quiz_participant(self, quiz_id: int, user_id: int):
        result = await self.session.execute(
            select(QuizParticipant).where(
                and_(
                    QuizParticipant.quiz_id == quiz_id,
                    QuizParticipant.user_id == user_id,
                )
            )
        )
        participant = result.scalar_one_or_none()
        if not participant:
            return None
        return QuizParticipantDetailResponse.model_validate(participant)
