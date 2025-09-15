from pydantic import BaseModel
from pydantic.generics import GenericModel
from typing import TypeVar, Generic

from app.schemas.user import UserDetailResponse

T = TypeVar("T")


class HealthCheckModel(BaseModel):
    status_code: int
    detail: str
    result: str


class ResponseModel(BaseModel):
    status_code: int
    message: str


class AuthResponseModel(BaseModel):
    status_code: int
    message: str
    token: str


class MeResponseModel(BaseModel):
    status_code: int
    me: UserDetailResponse


class ListResponse(GenericModel, Generic[T]):
    items: list[T]
    count: int
