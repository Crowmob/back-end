from sqlalchemy import select, func, and_, Integer, cast, case, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.repositories.base_repository import BaseRepository
from app.models.quiz_model import (
    QuizParticipant,
    Quiz,
    Records,
    Question,
    Answer,
    SelectedAnswers,
)


class QuizRepository(BaseRepository[Quiz]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Quiz)

    async def create_quiz_participant(self, quiz_id: int, user_id: int, score: int):
        quiz_participant = QuizParticipant(quiz_id=quiz_id, user_id=user_id)
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

        if quiz is None:
            return None

        return quiz

    async def get_all_quizzes(
        self,
        user_id: int,
        company_id: int | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ):
        last_completion_all_subq = (
            select(
                QuizParticipant.quiz_id,
                func.max(QuizParticipant.completed_at).label("last_completed_at"),
            )
            .group_by(QuizParticipant.quiz_id)
            .subquery()
        )

        last_completion_user_subq = (
            select(
                QuizParticipant.quiz_id,
                func.max(QuizParticipant.completed_at).label("user_last_completed"),
            )
            .where(QuizParticipant.user_id == user_id)
            .group_by(QuizParticipant.quiz_id)
            .subquery()
        )

        query = (
            select(
                Quiz.id,
                Quiz.title,
                Quiz.description,
                Quiz.frequency,
                last_completion_all_subq.c.last_completed_at,
                func.count().over().label("total_count"),
                case(
                    (
                        last_completion_user_subq.c.user_last_completed != None,
                        func.now()
                        >= last_completion_user_subq.c.user_last_completed
                        + cast(Quiz.frequency, Integer) * text("INTERVAL '1 day'"),
                    ),
                    else_=True,
                ).label("is_available"),
            )
            .outerjoin(
                last_completion_all_subq, last_completion_all_subq.c.quiz_id == Quiz.id
            )
            .outerjoin(
                last_completion_user_subq,
                last_completion_user_subq.c.quiz_id == Quiz.id,
            )
        )

        # Add conditional filter
        if company_id is not None:
            query = query.where(Quiz.company_id == company_id)

        # Apply pagination
        query = query.limit(limit or 5).offset(offset or 0)

        result = await self.session.execute(query)
        rows = result.all()

        if not rows:
            return [], 0

        total_count = rows[0][5]
        items = [row for row in rows]

        return items, total_count

    async def get_full_quiz_data_for_user(self, selected_answer_ids: list[int]):
        query = (
            select(
                Answer.text.label("answer_text"),
                Answer.is_correct,
                Question.text.label("question_text"),
                Quiz.title.label("quiz_title"),
                Quiz.description.label("quiz_description"),
            )
            .select_from(SelectedAnswers)
            .join(Answer, SelectedAnswers.answer_id == Answer.id)
            .join(Question, Answer.question_id == Question.id)
            .join(Quiz, Question.quiz_id == Quiz.id)
            .filter(SelectedAnswers.id.in_(selected_answer_ids))
        )

        result = await self.session.execute(query)
        rows = result.fetchall()

        return rows
