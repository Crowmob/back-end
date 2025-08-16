from pydantic import BaseModel, ConfigDict, Field

from app.schemas.base import IDMixin, TimestampMixin, PaginationMixin


class MembershipRequestSchema(BaseModel):
    type: str
    company_id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)


class MembershipSchema(BaseModel):
    role: str
    user_id: int
    company_id: int


class MembershipRequestDetailResponse(IDMixin, TimestampMixin, BaseModel):
    request_type: str = Field(..., alias="type")
    company_id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)


class MembershipDetailResponse(IDMixin, TimestampMixin, BaseModel):
    role: str
    user_id: int
    company_id: int
    model_config = ConfigDict(from_attributes=True)


class GetUserMembershipRequests(PaginationMixin, BaseModel):
    request_type: str
    user_id: int


class GetMembershipRequestsToCompany(PaginationMixin, BaseModel):
    request_type: str
    company_id: int


class GetCompaniesForUserRequest(PaginationMixin, BaseModel):
    user_id: int


class GetUsersInCompanyRequest(PaginationMixin, BaseModel):
    company_id: int


class GetAllAdminsRequest(PaginationMixin, BaseModel):
    company_id: int


class LeaveCompanyRequest(BaseModel):
    company_id: int
    user_id: int


class SendMembershipRequest(BaseModel):
    request_type: str
    company_id: int
    user_id: int
