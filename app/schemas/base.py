from datetime import datetime
from pydantic import BaseModel


class IDMixin(BaseModel):
    id: int


class TimestampMixin(BaseModel):
    created_at: datetime | None = None
    updated_at: datetime | None = None


class PaginationMixin(BaseModel):
    limit: int | None = None
    offset: int | None = None
