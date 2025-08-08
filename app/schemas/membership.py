from pydantic import BaseModel, ConfigDict

from app.schemas.base import IDMixin, TimestampMixin


class MembershipRequestDetailResponse(IDMixin, TimestampMixin, BaseModel):
    type: str
    from_id: int
    to_id: int
    model_config = ConfigDict(from_attributes=True)


class MembershipDetailResponse(IDMixin, TimestampMixin, BaseModel):
    user_id: int
    company_id: int
    model_config = ConfigDict(from_attributes=True)


class GetUserMembershipRequests(BaseModel):
    request_type: str
    user_id: int
    limit: int | None = None
    offset: int | None = None


class GetOwnerMembershipRequests(IDMixin, TimestampMixin, BaseModel):
    request_type: str
    owner_id: int
    limit: int | None = None
    offset: int | None = None


class GetMembershipsRequest(BaseModel):
    company_id: int
    limit: int | None = None
    offset: int | None = None
