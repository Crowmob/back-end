from fastapi import APIRouter, Depends

from app.schemas.company import (
    ListResponse,
    CompanyDetailResponse,
    GetAllCompaniesRequest,
)
from app.services.company import company_services

company_router = APIRouter(tags=["Company"], prefix="/company")


@company_router.get("/", response_model=ListResponse[CompanyDetailResponse])
async def get_all_companies(data: GetAllCompaniesRequest = Depends()):
    return await company_services.get_all_companies(data.limit, data.offset)


@company_router.get("/{company_id}", response_model=CompanyDetailResponse)
async def get_company_by_id(company_id: int):
    return await company_services.get_company_by_id(company_id)
