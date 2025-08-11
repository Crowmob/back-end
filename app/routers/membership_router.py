from fastapi import APIRouter, Depends, Body

from app.schemas.membership import (
    MembershipRequestDetailResponse,
    GetUserMembershipRequests,
    GetOwnerMembershipRequests,
    LeaveCompanyRequest,
    GetCompaniesForUserRequest,
    GetUsersInCompanyRequest,
    GetAllAdminsRequest,
)
from app.schemas.company import CompanyDetailResponse
from app.schemas.user import UserDetailResponse
from app.schemas.response_models import ListResponse, ResponseModel
from app.services.membership import membership_services

membership_router = APIRouter(tags=["Memberships"], prefix="/memberships")


@membership_router.get(
    "/requests/user", response_model=ListResponse[MembershipRequestDetailResponse]
)
async def get_user_membership_requests(data: GetUserMembershipRequests = Depends()):
    return await membership_services.get_membership_requests_for_user(
        data.request_type, data.user_id, data.limit, data.offset
    )


@membership_router.get(
    "/requests/owner", response_model=ListResponse[MembershipRequestDetailResponse]
)
async def get_owner_membership_requests(data: GetOwnerMembershipRequests = Depends()):
    return await membership_services.get_membership_requests_for_owner(
        data.request_type, data.owner_id, data.limit, data.offset
    )


@membership_router.get("/user", response_model=ListResponse[CompanyDetailResponse])
async def get_companies_for_user(data: GetCompaniesForUserRequest = Depends()):
    return await membership_services.get_companies_for_user(
        data.user_id, data.limit, data.offset
    )


@membership_router.get("/company", response_model=ListResponse[UserDetailResponse])
async def get_users_in_company(data: GetUsersInCompanyRequest = Depends()):
    return await membership_services.get_users_in_company(
        data.company_id, data.limit, data.offset
    )


@membership_router.get("/admins", response_model=ListResponse[UserDetailResponse])
async def get_all_admins(data: GetAllAdminsRequest = Depends()):
    return await membership_services.get_all_admins(
        data.company_id, data.limit, data.offset
    )


@membership_router.delete("/leave", response_model=ResponseModel)
async def leave_company(data: LeaveCompanyRequest = Body(...)):
    await membership_services.delete_membership(data.user_id, data.company_id)
    return ResponseModel(status_code=200, message="Leaved company successfully")
