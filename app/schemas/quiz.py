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


class QuestionWithAnswersSchema(BaseModel):
    text: str
    answers: list[AnswerSchema]

    @model_validator(mode="after")
    def validate_answers(self) -> "QuestionWithAnswersSchema":
        if not (2 <= len(self.answers) <= 4):
            raise QuizException(
                detail="Number of answers in question must be more than 1 and less than 5"
            )
        return self


class QuizWithQuestionsSchema(BaseModel):
    title: str
    description: str
    questions: list[QuestionWithAnswersSchema]

    @model_validator(mode="after")
    def validate_questions(self) -> "QuizWithQuestionsSchema":
        if len(self.questions) < 2:
            raise QuizException(detail="Quiz should have at least 2 questions")
        return self


class AnswerDetailResponse(IDMixin, AnswerSchema):
    model_config = ConfigDict(from_attributes=True)


class QuestionDetailResponse(IDMixin, QuestionSchema):
    answers: list[AnswerDetailResponse] | None = None


class QuizDetailResponse(IDMixin, TimestampMixin, QuizSchema):
    questions: list[QuestionDetailResponse] | None = None


class QuizCreateSchema(QuizSchema):
    company_id: int


class QuestionCreateSchema(QuestionSchema):
    quiz_id: int


class AnswerCreateSchema(AnswerSchema):
    question_id: int


class QuizUpdateSchema(BaseModel):
    title: str | None = None
    description: str | None = None


class QuestionUpdateSchema(BaseModel):
    text: str | None = None


class AnswerUpdateSchema(BaseModel):
    text: str | None = None
    is_correct: bool | None = None


class GetAllQuizzesRequest(BaseModel):
    company_id: int
    limit: int | None = None
    offset: int | None = None


class AllQuizzesResponse(BaseModel):
    quizzes: list[QuizDetailResponse]
