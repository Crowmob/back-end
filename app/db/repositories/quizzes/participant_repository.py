import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.base_repository import BaseRepository
from app.models.quiz_model import QuizParticipant

logger = logging.getLogger(__name__)


class QuizParticipantRepository(BaseRepository[QuizParticipant]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, QuizParticipant)
