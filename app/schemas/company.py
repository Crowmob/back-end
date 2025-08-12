from pydantic import BaseModel, ConfigDict
from pydantic.generics import GenericModel

from app.schemas.base import IDMixin


class CompanySchema(BaseModel):
    owner: int
    name: str
    description: str | None = None
    private: bool | None = False
    model_config = ConfigDict(from_attributes=True)


class CompanyIdResponse(BaseModel):
    id: int


class CompanyDetailResponse(IDMixin, BaseModel):
    owner: int
    name: str
    description: str | None = None
    private: bool | None = False
    is_owner: bool | None = False
    user_role: str | None = None
    model_config = ConfigDict(from_attributes=True)


class CompanyUpdateRequestModel(BaseModel):
    name: str | None = None
    description: str | None = None
    private: bool | None = False


class GetAllCompaniesRequest(BaseModel):
    limit: int | None = None
    offset: int | None = None
