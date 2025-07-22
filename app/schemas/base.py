from datetime import datetime
from pydantic import BaseModel


class IDMixin(BaseModel):
    id: int


class TimestampMixin(BaseModel):
    created_at: datetime
    updated_at: datetime
