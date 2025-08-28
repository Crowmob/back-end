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
from app.services.company import company_services
from app.utils.token import token_services
from app.services.user import user_services

company_router = APIRouter(tags=["Company"], prefix="/company")


@company_router.get("/", response_model=ListResponse[CompanyDetailResponse])
async def get_all_companies(
    data: GetAllCompaniesRequest = Depends(),
    email: Annotated[str | None, Depends(token_services.get_data_from_token)] = None,
):
    user_id = None
    if email:
        user = await user_services.get_user_by_email(email)
        user_id = user.id
    return await company_services.get_all_companies(data.limit, data.offset, user_id)


@company_router.get("/{company_id}", response_model=CompanyDetailResponse | None)
async def get_company_by_id(
    company_id: int,
    email: Annotated[str | None, Depends(token_services.get_data_from_token)],
):
    current_user = await user_services.get_user_by_email(email)
    company = await company_services.get_company_by_id(company_id, current_user.id)
    if company:
        owner = await user_services.get_user_by_id(company.owner)
        if current_user.email == owner.email:
            company.is_owner = True
    return company


@company_router.post("/", response_model=CompanyIdResponse)
async def create_company(data: CompanySchema = Body()):
    company_id = await company_services.create_company(
        data.owner, data.name, data.description, data.private
    )
    return CompanyIdResponse(id=company_id)


@company_router.put("/{company_id}", response_model=ResponseModel)
async def update_company(
    company_id: int,
    data: CompanyUpdateRequestModel = Body(),
    email: Annotated[str | None, Depends(token_services.get_data_from_token)] = "",
):
    current_user = await user_services.get_user_by_email(email)
    await company_services.update_company(
        company_id,
        data.name,
        data.description,
        data.private,
        current_user=current_user.id,
    )
    return ResponseModel(status_code=200, message="Company updated successfully")


@company_router.delete("/{company_id}", response_model=ResponseModel)
async def delete_company(
    company_id: int,
    email: Annotated[str | None, Depends(token_services.get_data_from_token)],
):
    current_user = await user_services.get_user_by_email(email)
    await company_services.delete_company(company_id, current_user.id)
    return ResponseModel(status_code=200, message="Company deleted successfully")
