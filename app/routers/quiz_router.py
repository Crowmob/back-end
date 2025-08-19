from fastapi import APIRouter, Depends

from app.schemas.quiz import QuizSchema, GetAllQuizzesRequest
from app.schemas.response_models import ListResponse
from app.services.quiz import quiz_services

quiz_router = APIRouter(tags=["Quizzes"], prefix="/quizzes")


@quiz_router.get("/", response_model=ListResponse[QuizSchema])
async def get_all_quizzes(data: GetAllQuizzesRequest = Depends()):
    return await quiz_services.get_all_quizzes(data)
