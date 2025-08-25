from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator

from app.core.exceptions.quiz_exceptions import QuizException
from app.schemas.base import TimestampMixin, IDMixin


class QuizSchema(BaseModel):
    title: str
    description: str


class QuestionSchema(BaseModel):
    text: str


class AnswerSchema(BaseModel):
    text: str
    is_correct: bool


class QuizParticipantSchema(BaseModel):
    quiz_id: int
    user_id: int
    completed_at: datetime


class QuestionWithAnswersSchema(QuestionSchema, BaseModel):
    answers: list[AnswerSchema]

    @model_validator(mode="after")
    def validate_answers(self) -> "QuestionWithAnswersSchema":
        if not (2 <= len(self.answers) <= 4):
            raise QuizException(
                detail="Number of answers in question must be more than 1 and less than 5"
            )
        return self


class QuizWithQuestionsSchema(QuizSchema, BaseModel):
    questions: list[QuestionWithAnswersSchema]

    @model_validator(mode="after")
    def validate_questions(self) -> "QuizWithQuestionsSchema":
        if len(self.questions) < 2:
            raise QuizException(detail="Quiz should have at least 2 questions")
        return self


class AnswerDetailResponse(IDMixin, AnswerSchema, BaseModel):
    model_config = ConfigDict(from_attributes=True)


class QuestionDetailResponse(IDMixin, QuestionSchema, BaseModel):
    pass


class QuizDetailResponse(IDMixin, QuizSchema, BaseModel):
    pass


class QuizParticipantDetailResponse(IDMixin, QuizParticipantSchema, BaseModel):
    pass


class QuizCreateSchema(QuizSchema, BaseModel):
    company_id: int


class QuestionCreateSchema(QuestionSchema, BaseModel):
    quiz_id: int


class AnswerCreateSchema(AnswerSchema, BaseModel):
    question_id: int


class QuizParticipantCreateSchema(BaseModel):
    quiz_id: int
    user_id: int


class RecordCreateSchema(BaseModel):
    participant_id: int
    score: int


class QuizUpdateSchema(BaseModel):
    title: str | None = None
    description: str | None = None


class QuestionUpdateSchema(BaseModel):
    text: str | None = None


class AnswerUpdateSchema(BaseModel):
    text: str | None = None
    is_correct: bool | None = None


class QuizParticipantUpdateSchema(BaseModel):
    completed_at: datetime | None = None


class GetAllQuizzesRequest(BaseModel):
    company_id: int
    limit: int | None = None
    offset: int | None = None


class AllQuizzesResponse(BaseModel):
    quizzes: list[QuizDetailResponse]
