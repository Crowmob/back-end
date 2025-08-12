from pydantic import BaseModel, ConfigDict, HttpUrl
from pydantic.generics import GenericModel

from app.schemas.base import IDMixin, TimestampMixin


class UserSchema(BaseModel):
    username: str | None = None
    email: str
    password: str | None = None
    about: str | None = None
    avatar: str | None = None
    model_config = ConfigDict(from_attributes=True)


class Username(BaseModel):
    name: str | None = None
    avatar: str | None = None


class SignUpRequestModel(BaseModel):
    username: str
    email: str
    password: str
    avatar: HttpUrl | None = None


class SignInRequestModel(BaseModel):
    email: str
    password: str


class UserUpdateRequestModel(BaseModel):
    username: str | None = None
    password: str | None = None
    about: str | None = None
    model_config = ConfigDict(from_attributes=True)


class GetAllUsersRequestModel(BaseModel):
    limit: int | None = None
    offset: int | None = None


class UserDetailResponse(IDMixin, TimestampMixin, BaseModel):
    username: str | None = None
    email: str
    about: str | None = None
    avatar: str | None = None
    current_user: bool | None = False
    model_config = ConfigDict(from_attributes=True)


class MemberDetailResponse(IDMixin, TimestampMixin, BaseModel):
    username: str | None = None
    email: str
    about: str | None = None
    avatar: str | None = None
    role: str | None = None
    current_user: bool | None = False
    model_config = ConfigDict(from_attributes=True)
