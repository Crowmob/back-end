from pydantic import BaseModel


class AdminActionRequest(BaseModel):
    user_id: int
    company_id: int
