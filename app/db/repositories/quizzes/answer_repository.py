from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.base_repository import BaseRepository
from app.models.quiz_model import (
    Answer,
    SelectedAnswers,
    QuizParticipant,
    Records,
    Quiz,
)


class AnswerRepository(BaseRepository[Answer]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Answer)

    async def create_selected_answers(self, record_id: int, data: list[int]):
        selected_answers = [
            SelectedAnswers(record_id=record_id, answer_id=answer) for answer in data
        ]
        self.session.add_all(selected_answers)
        await self.session.flush()
        ids = [answer.id for answer in selected_answers]
        return ids

    async def get_missing_answers(
        self,
        answer_ids: list[int],
        user_id: int,
        quiz_id: int = None,
        company_id: int = None,
    ):
        query = (
            select(SelectedAnswers)
            .join(Records, SelectedAnswers.record_id == Records.id)
            .join(QuizParticipant, Records.participant_id == QuizParticipant.id)
            .join(Quiz, QuizParticipant.quiz_id == Quiz.id)
            .filter(QuizParticipant.user_id == user_id)
        )

        if quiz_id:
            query = query.filter(QuizParticipant.quiz_id == quiz_id)

        if company_id:
            query = query.filter(Quiz.company_id == company_id)

        if answer_ids:
            query = query.filter(~SelectedAnswers.id.in_(answer_ids))

        result = await self.session.execute(query)
        rows = result.scalars().all()
        return rows
