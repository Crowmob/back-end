from typing import Generic, TypeVar
from pydantic import BaseModel, ConfigDict
from pydantic.generics import GenericModel

from app.schemas.base import IDMixin

T = TypeVar("T")


class CompanySchema(BaseModel):
    name: str
    description: str | None = None
    private: bool | None = False
    model_config = ConfigDict(from_attributes=True)


class CompanyDetailResponse(IDMixin, BaseModel):
    name: str
    description: str | None = None
    private: bool | None = False
    model_config = ConfigDict(from_attributes=True)


class CompanyUpdateRequestModel(BaseModel):
    name: str | None = None
    description: str | None = None
    private: bool | None = False


class ListResponse(GenericModel, Generic[T]):
    items: list[T]
    count: int


class GetAllCompaniesRequest(BaseModel):
    limit: int | None = None
    offset: int | None = None
