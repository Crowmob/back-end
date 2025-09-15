from datetime import datetime

from pydantic import BaseModel

from app.core.enums.enums import NotificationStatus
from app.schemas.base import IDMixin


class NotificationSchema(BaseModel):
    status: NotificationStatus
    created_at: datetime = None
    user_id: int | None = None
    company_id: int | None = None
    message: str


class NotificationDetailResponse(IDMixin, NotificationSchema, BaseModel):
    pass


class GetAllNotificationsRequest(BaseModel):
    limit: int
    offset: int
