from fastapi import APIRouter, Depends, Header

from app.schemas.quiz import GetAllQuizzesRequest, QuizDetailResponse
from app.schemas.response_models import ListResponse, ResponseModel
from app.services.quiz import quiz_services
from app.services.user import user_services
from app.utils.token import token_services

quiz_router = APIRouter(tags=["Quizzes"], prefix="/quizzes")


@quiz_router.get("/", response_model=ListResponse[QuizDetailResponse])
async def get_all_quizzes(data: GetAllQuizzesRequest = Depends()):
    return await quiz_services.get_all_quizzes(data)


@quiz_router.post("/{quiz_id}", response_model=ResponseModel)
async def quiz_submit(quiz_id: int, score: int, authorization: str = Header(...)):
    token = authorization.removeprefix("Bearer ")
    token_data = await token_services.get_data_from_token(token)
    current_user = await user_services.get_user_by_email(
        token_data["http://localhost:8000/email"]
    )
    await quiz_services.quiz_submit(quiz_id, current_user.id, score)
