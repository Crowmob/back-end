from pydantic import BaseModel

from app.schemas.user import UserDetailResponse


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
