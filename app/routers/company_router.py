from typing import Annotated

from fastapi import APIRouter, Body, Depends, Header

from app.schemas.company import (
    CompanyDetailResponse,
    GetAllCompaniesRequest,
    CompanySchema,
    CompanyIdResponse,
    CompanyUpdateRequestModel,
)
from app.schemas.response_models import ResponseModel, ListResponse
from app.schemas.user import UserSchema, UserDetailResponse
from app.services.company import get_company_service, CompanyServices
from app.utils.token import token_services

company_router = APIRouter(tags=["Company"], prefix="/company")


@company_router.get("/", response_model=ListResponse[CompanyDetailResponse])
async def get_all_companies(
    data: GetAllCompaniesRequest = Depends(),
    current_user: Annotated[
        UserDetailResponse | None, Depends(token_services.get_data_from_token)
    ] = None,
    company_service: CompanyServices = Depends(get_company_service),
):
    return await company_service.get_all_companies(
        data.limit, data.offset, current_user.id
    )


@company_router.get("/{company_id}", response_model=CompanyDetailResponse)
async def get_company_by_id(
    company_id: int,
    current_user: Annotated[
        UserDetailResponse | None, Depends(token_services.get_data_from_token)
    ] = None,
    company_service: CompanyServices = Depends(get_company_service),
):
    return await company_service.get_company_by_id(
        company_id, current_user.id, current_user.email
    )


@company_router.post("/", response_model=CompanyIdResponse)
async def create_company(
    data: CompanySchema = Body(),
    company_service: CompanyServices = Depends(get_company_service),
    _: Annotated[
        UserDetailResponse | None, Depends(token_services.get_data_from_token)
    ] = None,
):
    company_id = await company_service.create_company(
        data.owner, data.name, data.description, data.private
    )
    return CompanyIdResponse(id=company_id)


@company_router.put("/{company_id}", response_model=ResponseModel)
async def update_company(
    company_id: int,
    data: CompanyUpdateRequestModel = Body(),
    current_user: Annotated[
        UserDetailResponse | None, Depends(token_services.get_data_from_token)
    ] = None,
    company_service: CompanyServices = Depends(get_company_service),
):
    await company_service.update_company(
        company_id,
        data.name,
        data.description,
        data.private,
        current_user.id,
        current_user.email,
    )
    return ResponseModel(status_code=200, message="Company updated successfully")


@company_router.delete("/{company_id}", response_model=ResponseModel)
async def delete_company(
    company_id: int,
    current_user: Annotated[
        UserDetailResponse | None, Depends(token_services.get_data_from_token)
    ] = None,
    company_service: CompanyServices = Depends(get_company_service),
):
    await company_service.delete_company(
        company_id, current_user.id, current_user.email
    )
    return ResponseModel(status_code=200, message="Company deleted successfully")
