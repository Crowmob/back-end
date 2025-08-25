from fastapi import APIRouter, Depends, Header, Body

from app.schemas.quiz import (
    GetAllQuizzesRequest,
    QuizDetailResponse,
    QuizWithQuestionsSchema,
    QuizSubmitRequest,
)
from app.schemas.response_models import ListResponse, ResponseModel
from app.services.quiz import quiz_services
from app.services.user import user_services
from app.utils.token import token_services

quiz_router = APIRouter(tags=["Quizzes"], prefix="/quizzes")


@quiz_router.get("/", response_model=ListResponse[QuizDetailResponse])
async def get_all_quizzes(data: GetAllQuizzesRequest = Depends()):
    return await quiz_services.get_all_quizzes(data.company_id, data.limit, data.offset)


@quiz_router.get("/{quiz_id}:{company_id}", response_model=QuizWithQuestionsSchema)
async def get_quiz_by_id(quiz_id: int, company_id: int):
    return await quiz_services.get_quiz_by_id(quiz_id, company_id)


@quiz_router.post("/{company_id}/{quiz_id}", response_model=ResponseModel)
async def create_quiz(
    company_id: int, quiz_id: int | str, data: QuizWithQuestionsSchema = Body(...)
):
    await quiz_services.create_quiz(
        company_id, None if quiz_id == "null" else int(quiz_id), data
    )
    return ResponseModel(status_code=200, message="Created quiz")


@quiz_router.post("/{quiz_id}", response_model=ResponseModel)
async def quiz_submit(
    data: QuizSubmitRequest = Body(...), authorization: str = Header(...)
):
    token = authorization.removeprefix("Bearer ")
    token_data = await token_services.get_data_from_token(token)
    current_user = await user_services.get_user_by_email(
        token_data["http://localhost:8000/email"]
    )
    await quiz_services.quiz_submit(current_user.id, data)


@quiz_router.delete("/{quiz_id}", response_model=ResponseModel)
async def delete_quiz(quiz_id: int):
    await quiz_services.delete_quiz(quiz_id)
    return ResponseModel(status_code=200, message="Deleted quiz")
