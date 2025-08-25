from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.repositories.base_repository import BaseRepository
from app.models.quiz_model import QuizParticipant, Quiz, Records, Question
from app.schemas.quiz import (
    QuizDetailResponse,
    QuizWithQuestionsSchema,
    QuestionWithAnswersSchema,
    AnswerSchema,
)
from app.schemas.response_models import ListResponse


class QuizRepository(BaseRepository[Quiz]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Quiz)

    async def create_quiz_participant(self, quiz_id: int, user_id: int, score: int):
        quiz_participant = QuizParticipant(quiz_id, user_id)
        self.session.add(quiz_participant)
        await self.session.flush()
        await self.session.refresh(quiz_participant)
        record = Records(participant_id=quiz_participant.id, score=score)
        self.session.add(record)

    async def get_quiz_by_id(self, quiz_id: int, company_id: int):
        stmt = (
            select(Quiz)
            .where(Quiz.id == quiz_id, Quiz.company_id == company_id)
            .options(selectinload(Quiz.questions).selectinload(Question.answers))
        )
        result = await self.session.execute(stmt)
        quiz = result.scalar_one_or_none()

        return QuizWithQuestionsSchema(
            title=quiz.title,
            description=quiz.description or "",
            questions=[
                QuestionWithAnswersSchema(
                    text=q.text,
                    answers=[
                        AnswerSchema(text=a.text, is_correct=a.is_correct)
                        for a in q.answers
                    ],
                )
                for q in quiz.questions
            ],
        )

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
