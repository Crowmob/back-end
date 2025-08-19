from pydantic import BaseModel, ConfigDict

from app.schemas.base import TimestampMixin, IDMixin


class QuizSchema(IDMixin, TimestampMixin, BaseModel):
    title: str
    description: str


class QuestionSchema(IDMixin, BaseModel):
    text: str


class Answer(BaseModel):
    text: str
    is_correct: bool


class AnswerSchema(IDMixin, Answer, BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Question(BaseModel):
    text: str
    answers: list[Answer]


class Quiz(BaseModel):
    title: str
    description: str
    questions: list[Question]


class CreateQuizSchema(BaseModel):
    title: str
    description: str
    company_id: int


class CreateAnswerSchema(BaseModel):
    text: str
    is_correct: bool
    question_id: int


class CreateQuestionSchema(BaseModel):
    text: str
    quiz_id: int


class AllQuizzesResponse(BaseModel):
    quizzes: list[Quiz]


class QuizUpdateModel(BaseModel):
    title: str | None = None
    description: str | None = None


class QuestionUpdateModel(BaseModel):
    text: str | None = None


class AnswerUpdateModel(BaseModel):
    text: str | None = None
    is_correct: bool


class GetAllQuizzesRequest(BaseModel):
    company_id: int
    limit: int | None = None
    offset: int | None = None
