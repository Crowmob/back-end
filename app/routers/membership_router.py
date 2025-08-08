from fastapi import APIRouter, Depends

from app.schemas.membership import (
    MembershipRequestDetailResponse,
    GetUserMembershipRequests,
    GetOwnerMembershipRequests,
    GetMembershipsRequest,
    MembershipDetailResponse,
)
from app.schemas.response_models import ListResponse, ResponseModel
from app.services.membership import membership_services

membership_router = APIRouter(tags=["Memberships"], prefix="/memberships")


@membership_router.get(
    "/user", response_model=ListResponse[MembershipRequestDetailResponse]
)
async def get_user_membership_requests(data: GetUserMembershipRequests = Depends()):
    return await membership_services.get_membership_requests_for_user(
        data.request_type, data.user_id, data.limit, data.offset
    )


@membership_router.get(
    "/owner", response_model=ListResponse[MembershipRequestDetailResponse]
)
async def get_owner_membership_requests(data: GetUserMembershipRequests = Depends()):
    return await membership_services.get_membership_requests_for_owner(
        data.request_type, data.owner_id, data.limit, data.offset
    )


@membership_router.get("/", response_model=ListResponse[MembershipDetailResponse])
async def get_all_memberships(data: GetUserMembershipRequests = Depends()):
    return await membership_services.get_all_memberships(
        data.company_id, data.limit, data.offset
    )
