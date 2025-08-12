from pydantic import BaseModel, ConfigDict, Field

from app.schemas.base import IDMixin, TimestampMixin


class MembershipRequestDetailResponse(IDMixin, TimestampMixin, BaseModel):
    request_type: str = Field(..., alias="type")
    from_id: int
    to_id: int
    model_config = ConfigDict(from_attributes=True)


class MembershipDetailResponse(IDMixin, TimestampMixin, BaseModel):
    role: str
    user_id: int
    company_id: int
    model_config = ConfigDict(from_attributes=True)


class GetUserMembershipRequests(BaseModel):
    request_type: str
    user_id: int
    limit: int | None = None
    offset: int | None = None


class GetMembershipRequestsToCompany(BaseModel):
    request_type: str
    company_id: int
    limit: int | None = None
    offset: int | None = None


class GetCompaniesForUserRequest(BaseModel):
    user_id: int
    limit: int | None = None
    offset: int | None = None


class GetUsersInCompanyRequest(BaseModel):
    company_id: int
    limit: int | None = None
    offset: int | None = None


class GetAllAdminsRequest(BaseModel):
    company_id: int
    limit: int | None = None
    offset: int | None = None


class LeaveCompanyRequest(BaseModel):
    company_id: int
    user_id: int


class SendMembershipRequest(BaseModel):
    request_type: str
    company_id: int
    user_id: int
