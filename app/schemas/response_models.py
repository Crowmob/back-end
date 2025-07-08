from pydantic import BaseModel


class UserResponse(BaseModel):
    status_code: int
    detail: str
    result: str