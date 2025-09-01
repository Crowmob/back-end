from typing import Annotated

from fastapi import APIRouter, Depends, Body

from app.schemas.membership import (
    MembershipDetailResponse,
    SendMembershipRequest,
    GetUserMembershipRequests,
    GetMembershipRequestsToCompany,
    LeaveCompanyRequest,
    GetCompaniesForUserRequest,
    GetUsersInCompanyRequest,
    AcceptMembershipRequest,
    GetMembershipRequest,
    CancelMembershipRequest,
)
from app.schemas.company import CompanyDetailResponse
from app.schemas.user import MemberDetailResponse, UserDetailResponse
from app.schemas.response_models import ListResponse, ResponseModel
from app.services.membership import get_membership_service, MembershipServices
from app.utils.token import token_services

membership_router = APIRouter(tags=["Memberships"], prefix="/memberships")


@membership_router.get("/", response_model=MembershipDetailResponse | None)
async def get_membership(
    data: GetMembershipRequest = Depends(),
    membership_service: MembershipServices = Depends(get_membership_service),
    email: Annotated[str | None, Depends(token_services.get_data_from_token)] = None,
):
    return await membership_service.get_membership(data.user_id, data.company_id, email)


@membership_router.get(
    "/requests/user", response_model=ListResponse[CompanyDetailResponse]
)
async def get_user_requests(
    data: GetUserMembershipRequests = Depends(),
    membership_service: MembershipServices = Depends(get_membership_service),
    email: Annotated[str | None, Depends(token_services.get_data_from_token)] = None,
):
    return await membership_service.get_membership_requests_for_user(
        data.request_type, data.user_id, data.limit, data.offset, email
    )


@membership_router.get(
    "/requests/company", response_model=ListResponse[UserDetailResponse]
)
async def get_requests_to_company(
    data: GetMembershipRequestsToCompany = Depends(),
    membership_service: MembershipServices = Depends(get_membership_service),
    email: Annotated[str | None, Depends(token_services.get_data_from_token)] = None,
):
    return await membership_service.get_membership_requests_to_company(
        data.request_type, data.company_id, data.limit, data.offset, email
    )


@membership_router.get("/user", response_model=ListResponse[CompanyDetailResponse])
async def get_companies_for_user(
    data: GetCompaniesForUserRequest = Depends(),
    membership_service: MembershipServices = Depends(get_membership_service),
    email: Annotated[str | None, Depends(token_services.get_data_from_token)] = None,
):
    return await membership_service.get_companies_for_user(
        data.user_id, data.limit, data.offset, email
    )


@membership_router.get("/company", response_model=ListResponse[MemberDetailResponse])
async def get_users_in_company(
    data: GetUsersInCompanyRequest = Depends(),
    membership_service: MembershipServices = Depends(get_membership_service),
    email: Annotated[str | None, Depends(token_services.get_data_from_token)] = None,
):
    return await membership_service.get_users_in_company(
        data.company_id, data.limit, data.offset, email
    )


@membership_router.post("/request", response_model=ResponseModel)
async def send_membership_request(
    data: SendMembershipRequest = Body(...),
    membership_service: MembershipServices = Depends(get_membership_service),
    email: Annotated[str | None, Depends(token_services.get_data_from_token)] = None,
):
    await membership_service.send_membership_request(
        data.request_type, data.company_id, data.user_id, email
    )
    return ResponseModel(
        status_code=200, message="Sent membership request successfully"
    )


@membership_router.delete("/delete", response_model=ResponseModel)
async def delete_membership(
    data: LeaveCompanyRequest = Body(...),
    membership_service: MembershipServices = Depends(get_membership_service),
    email: Annotated[str | None, Depends(token_services.get_data_from_token)] = None,
):
    await membership_service.delete_membership(data.user_id, data.company_id, email)
    return ResponseModel(status_code=200, message="Leaved company successfully")


@membership_router.post("/accept", response_model=ResponseModel)
async def accept_membership_request(
    data: AcceptMembershipRequest = Body(...),
    membership_service: MembershipServices = Depends(get_membership_service),
    email: Annotated[str | None, Depends(token_services.get_data_from_token)] = None,
):
    await membership_service.accept_membership_request(
        data.request_type, data.user_id, data.company_id, email
    )
    return ResponseModel(
        status_code=200, message="Accepted membership request successfully"
    )


@membership_router.delete("/request/delete", response_model=ResponseModel)
async def delete_membership_request(
    data: CancelMembershipRequest = Body(...),
    membership_service: MembershipServices = Depends(get_membership_service),
    email: Annotated[str | None, Depends(token_services.get_data_from_token)] = None,
):
    await membership_service.cancel_membership_request(
        data.user_id, data.company_id, email
    )
    return ResponseModel(
        status_code=200, message="Canceled membership request successfully"
    )
