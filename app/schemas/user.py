from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict
from pydantic.generics import GenericModel

from app.schemas.base import IDMixin, TimestampMixin

T = TypeVar("T")


class UserSchema(BaseModel):
    username: str
    email: str
    password: str
    model_config = ConfigDict(from_attributes=True)


class SignUpRequestModel(BaseModel):
    username: str
    email: str
    password: str


class SignInRequestModel(BaseModel):
    username: str
    password: str


class UserUpdateRequestModel(BaseModel):
    username: str | None = None
    email: str | None = None
    password: str | None = None
    model_config = ConfigDict(from_attributes=True)


class GetAllUsersRequestModel(BaseModel):
    limit: int | None = None
    offset: int | None = None


class ListResponse(GenericModel, Generic[T]):
    items: list[T]
    count: int


class UserDetailResponse(IDMixin, TimestampMixin, BaseModel):
    username: str
    email: str
    model_config = ConfigDict(from_attributes=True)
