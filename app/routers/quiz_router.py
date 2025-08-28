import csv
from io import StringIO
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Body
from fastapi.responses import JSONResponse, StreamingResponse

from app.core.enums.enums import FileFormat
from app.core.exceptions.auth_exceptions import UnauthorizedException
from app.schemas.quiz import (
    GetAllQuizzesRequest,
    QuizDetailResponse,
    QuizWithQuestionsSchema,
    QuizSubmitRequest,
    QuizWithQuestionsDetailResponse,
)
from app.schemas.response_models import ListResponse, ResponseModel
from app.services.export_service import export_service
from app.services.quiz import quiz_services
from app.services.user import user_services
from app.utils.token import token_services

quiz_router = APIRouter(tags=["Quizzes"], prefix="/quizzes")


@quiz_router.get("/", response_model=ListResponse[QuizDetailResponse])
async def get_all_quizzes(
    data: GetAllQuizzesRequest = Depends(),
    email: Annotated[str | None, Depends(token_services.get_data_from_token)] = None,
):
    user = await user_services.get_user_by_email(email)
    return await quiz_services.get_all_quizzes(
        data.company_id, user.id, data.limit, data.offset
    )


@quiz_router.get(
    "/{quiz_id}/{company_id}", response_model=QuizWithQuestionsDetailResponse | None
)
async def get_quiz_by_id(
    quiz_id: int,
    company_id: int,
    email: Annotated[str | None, Depends(token_services.get_data_from_token)] = None,
):
    if email:
        return await quiz_services.get_quiz_by_id(quiz_id, company_id)
    else:
        raise UnauthorizedException(detail="Unauthorized")


@quiz_router.post("/{company_id}/{quiz_id}", response_model=ResponseModel)
async def create_quiz(
    company_id: int, quiz_id: int | str, data: QuizWithQuestionsSchema = Body(...)
):
    await quiz_services.create_quiz(
        company_id, None if quiz_id == "null" else int(quiz_id), data
    )
    return ResponseModel(status_code=200, message="Created quiz")


@quiz_router.post("/{quiz_id}", response_model=ResponseModel)
async def quiz_submit(data: QuizSubmitRequest = Body(...)):
    await quiz_services.quiz_submit(data)
    return ResponseModel(status_code=200, message="Submitted quiz")


@quiz_router.delete("/{quiz_id}", response_model=ResponseModel)
async def delete_quiz(quiz_id: int):
    await quiz_services.delete_quiz(quiz_id)
    return ResponseModel(status_code=200, message="Deleted quiz")


@quiz_router.get("/export")
async def export_all_quizzes_data_for_user(
    export_format: str,
    email: Annotated[str | None, Depends(token_services.get_data_from_token)] = None,
):
    if email:
        user = await user_services.get_user_by_email(email)
        quiz_data = await quiz_services.get_quiz_data_for_user(user.id)

        return export_service.export_data(
            quiz_data, export_format, f"quizzes_user_{user.email}"
        )
    else:
        raise UnauthorizedException(detail="Unauthorized")


@quiz_router.get("/export/{user_id}/{company_id}")
async def export_all_quizzes_data_for_user_in_company(
    export_format: str,
    user_id: int,
    company_id: int,
    email: Annotated[str | None, Depends(token_services.get_data_from_token)] = None,
):
    if email:
        user = await user_services.get_user_by_id(user_id)
        quiz_data = await quiz_services.get_quiz_data_for_user(
            user_id, company_id=company_id
        )

        return export_service.export_data(
            quiz_data, export_format, f"quizzes_user_{user.email}"
        )
    else:
        raise UnauthorizedException(detail="Unauthorized")


@quiz_router.get("/export/{user_id}/{company_id}/{quiz_id}")
async def export_single_quiz_data_for_user_in_company(
    quiz_id: int,
    user_id: int,
    company_id,
    export_format: str,
    email: Annotated[str | None, Depends(token_services.get_data_from_token)] = None,
):
    if email:
        user = await user_services.get_user_by_id(user_id)
        quiz_data = await quiz_services.get_quiz_data_for_user(
            user_id, quiz_id, company_id
        )

        return export_service.export_data(
            quiz_data, export_format, f"quiz_{quiz_id}_user_{user.email}"
        )
    else:
        raise UnauthorizedException(detail="Unauthorized")
