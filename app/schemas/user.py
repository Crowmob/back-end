from pydantic import BaseModel, ConfigDict
from pydantic.generics import GenericModel
from datetime import date
from typing import Optional, List, Generic, TypeVar

T = TypeVar("T")


class UserSchema(BaseModel):
    username: str
    email: str
    password: str
    date_of_birth: date
    gender: str
    model_config = ConfigDict(from_attributes=True)


class SignUpRequestModel(BaseModel):
    username: str
    email: str
    password: str
    date_of_birth: date
    gender: str


class SignInRequestModel(BaseModel):
    username: str
    password: str


class UserUpdateRequestModel(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    date_of_birth: Optional[date] = None
    model_config = ConfigDict(from_attributes=True)


class GetAllUsersRequestModel(BaseModel):
    limit: Optional[int] = None
    offset: Optional[int] = None


class ListResponse(GenericModel, Generic[T]):
    items: List[T]
    count: int


class UserDetailResponse(BaseModel):
    id: int
    username: str
    email: str
    date_of_birth: date
    gender: str
    created_at: date
    model_config = ConfigDict(from_attributes=True)
