from pydantic import BaseModel


class UserResponseSchema(BaseModel):
    status_code: int
    detail: str
    result: str