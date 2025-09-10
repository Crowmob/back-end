from typing import Annotated

from fastapi import APIRouter, Depends, Body

from app.core.enums.enums import FileFormat
from app.schemas.quiz import (
    GetAllQuizzesRequest,
    QuizDetailResponse,
    QuizWithQuestionsSchema,
    QuizSubmitRequest,
    QuizWithQuestionsDetailResponse,
    QuizAverageResponse,
    QuizAverageRequest,
    QuizUpdateRequest,
)
from app.schemas.response_models import ListResponse, ResponseModel
from app.schemas.user import UserDetailResponse
from app.services.export_service import get_export_service, ExportService
from app.services.quiz import get_quiz_service, QuizServices
from app.utils.token import token_services

quiz_router = APIRouter(tags=["Quizzes"], prefix="/quizzes")


@quiz_router.get("/", response_model=ListResponse[QuizDetailResponse])
async def get_all_quizzes(
    data: GetAllQuizzesRequest = Depends(),
    current_user: Annotated[
        UserDetailResponse | None, Depends(token_services.get_data_from_token)
    ] = None,
    quiz_service: QuizServices = Depends(get_quiz_service),
):
    return await quiz_service.get_all_quizzes(
        data.company_id, data.limit, data.offset, current_user.id
    )


@quiz_router.get("/score/{user_id}", response_model=QuizAverageResponse)
async def get_average_score_for_user(
    user_id: int,
    data: QuizAverageRequest = Depends(),
    quiz_service: QuizServices = Depends(get_quiz_service),
    _: Annotated[str | None, Depends(token_services.get_data_from_token)] = None,
):
    return await quiz_service.get_average_score_in_system(
        user_id, data.from_date, data.till_date
    )


@quiz_router.get("/score/{user_id}/{company_id}", response_model=QuizAverageResponse)
async def get_average_score_for_user_in_company(
    user_id: int,
    company_id: int,
    data: QuizAverageRequest = Depends(),
    quiz_service: QuizServices = Depends(get_quiz_service),
    _: Annotated[
        UserDetailResponse | None, Depends(token_services.get_data_from_token)
    ] = None,
):
    return await quiz_service.get_average_score_in_company(
        user_id,
        company_id,
        data.from_date,
        data.till_date,
    )


@quiz_router.get(
    "/{quiz_id}/{company_id}", response_model=QuizWithQuestionsDetailResponse | None
)
async def get_quiz_by_id(
    quiz_id: int,
    company_id: int,
    _: Annotated[
        UserDetailResponse | None, Depends(token_services.get_data_from_token)
    ] = None,
    quiz_service: QuizServices = Depends(get_quiz_service),
):
    return await quiz_service.get_quiz_by_id(quiz_id, company_id)


@quiz_router.post("/{company_id}", response_model=ResponseModel)
async def create_quiz(
    company_id: int,
    data: QuizWithQuestionsSchema = Body(...),
    quiz_service: QuizServices = Depends(get_quiz_service),
    _: Annotated[
        UserDetailResponse | None, Depends(token_services.get_data_from_token)
    ] = None,
):
    await quiz_service.create_quiz(company_id, data)
    return ResponseModel(status_code=200, message="Created quiz")


@quiz_router.put("/{quiz_id}", response_model=ResponseModel)
async def update_quiz(
    quiz_id: int,
    data: QuizUpdateRequest = Body(...),
    quiz_service: QuizServices = Depends(get_quiz_service),
    _: Annotated[
        UserDetailResponse | None, Depends(token_services.get_data_from_token)
    ] = None,
):
    await quiz_service.update_quiz(
        quiz_id,
        data.title,
        data.description,
        data.frequency,
        data.updated_questions,
        data.updated_answers,
    )
    return ResponseModel(status_code=200, message="Created quiz")


@quiz_router.post("/{quiz_id}", response_model=ResponseModel)
async def quiz_submit(
    data: QuizSubmitRequest = Body(...),
    quiz_service: QuizServices = Depends(get_quiz_service),
    current_user: Annotated[
        UserDetailResponse | None, Depends(token_services.get_data_from_token)
    ] = None,
):
    await quiz_service.quiz_submit(data, current_user.id)
    return ResponseModel(status_code=200, message="Submitted quiz")


@quiz_router.delete("/{quiz_id}", response_model=ResponseModel)
async def delete_quiz(
    quiz_id: int,
    quiz_service: QuizServices = Depends(get_quiz_service),
    _: Annotated[
        UserDetailResponse | None, Depends(token_services.get_data_from_token)
    ] = None,
):
    await quiz_service.delete_quiz(quiz_id)
    return ResponseModel(status_code=200, message="Deleted quiz")


@quiz_router.get("/export")
async def export_all_quizzes_data_for_user(
    export_format: FileFormat,
    current_user: Annotated[
        UserDetailResponse | None, Depends(token_services.get_data_from_token)
    ] = None,
    quiz_service: QuizServices = Depends(get_quiz_service),
    export_service: ExportService = Depends(get_export_service),
):
    quiz_data = await quiz_service.get_quiz_data_for_user(
        current_user_id=current_user.id
    )
    return export_service.export_data(
        quiz_data, export_format, f"quizzes_user_{current_user.email}"
    )


@quiz_router.get("/export/{user_id}/{company_id}")
async def export_all_quizzes_data_for_user_in_company(
    export_format: FileFormat,
    user_id: int,
    company_id: int,
    current_user: Annotated[
        UserDetailResponse | None, Depends(token_services.get_data_from_token)
    ] = None,
    quiz_service: QuizServices = Depends(get_quiz_service),
    export_service: ExportService = Depends(get_export_service),
):
    quiz_data = await quiz_service.get_quiz_data_for_user(
        user_id=user_id, company_id=company_id, current_user_id=current_user.id
    )
    return export_service.export_data(
        quiz_data, export_format, f"quizzes_user_{current_user.email}"
    )


@quiz_router.get("/export/{user_id}/{company_id}/{quiz_id}")
async def export_single_quiz_data_for_user_in_company(
    quiz_id: int,
    user_id: int,
    company_id,
    export_format: FileFormat,
    current_user: Annotated[
        UserDetailResponse | None, Depends(token_services.get_data_from_token)
    ] = None,
    quiz_service: QuizServices = Depends(get_quiz_service),
    export_service: ExportService = Depends(get_export_service),
):
    quiz_data = await quiz_service.get_quiz_data_for_user(
        user_id=user_id,
        quiz_id=quiz_id,
        company_id=company_id,
        current_user_id=current_user.id,
    )
    return export_service.export_data(
        quiz_data, export_format, f"quiz_{quiz_id}_user_{current_user.email}"
    )
