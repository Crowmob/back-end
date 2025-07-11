from pydantic import BaseModel
from datetime import date
from typing import Optional, List


class UserSchema(BaseModel):
    username: str
    email: str
    password: str
    date_of_birth: date
    gender: str


class SignInRequestModel(BaseModel):
    username: str
    email: str
    password: str
    date_of_birth: date
    gender: str


class SignUpRequestModel(BaseModel):
    username: str
    password: str


class UserUpdateRequestModel(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    date_of_birth: Optional[date] = None


class UsersListResponse(BaseModel):
    users: List[UserSchema]


class UserDetailResponse(BaseModel):
    id: int
    username: str
    email: str
    date_of_birth: date
    gender: str
    created_at: date
