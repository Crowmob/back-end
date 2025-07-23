from pydantic import BaseModel


class HealthCheckModel(BaseModel):
    status_code: int
    detail: str
    result: str


class ResponseModel(BaseModel):
    status_code: int
    message: str
