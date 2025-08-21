from datetime import datetime

from sqlalchemy import ForeignKey, String, Integer, func, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IDMixin, TimestampMixin


class Quiz(Base, IDMixin, TimestampMixin):
    __tablename__ = "quizzes"

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)


class QuizParticipant(Base, IDMixin):
    __tablename__ = "quiz_participants"

    quiz_id: Mapped[int] = mapped_column(
        ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Records(Base, IDMixin):
    __tablename__ = "records"

    score: Mapped[int] = mapped_column(Integer, nullable=False)
    participant_id: Mapped[int] = mapped_column(
        ForeignKey("quiz_participants.id", ondelete="CASCADE"), nullable=False
    )


class Question(Base, IDMixin):
    __tablename__ = "questions"

    quiz_id: Mapped[int] = mapped_column(
        ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False
    )
    text: Mapped[str] = mapped_column(String(512), nullable=False)
    correct_answers: Mapped[int] = mapped_column(Integer, nullable=False)


class Answer(Base, IDMixin):
    __tablename__ = "answers"

    text: Mapped[str] = mapped_column(String(512), nullable=False)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"), nullable=False
    )
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
