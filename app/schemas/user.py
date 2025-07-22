from pydantic import BaseModel, ConfigDict
from pydantic.generics import GenericModel
from datetime import datetime
from typing import Optional, List, Generic, TypeVar

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
    email: str
    password: str


class UserUpdateRequestModel(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
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
    password: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
