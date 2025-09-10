from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends

from app.schemas.notification import (
    NotificationDetailResponse,
    GetAllNotificationsRequest,
)
from app.schemas.response_models import ListResponse, ResponseModel
from app.schemas.user import UserDetailResponse
from app.services.notification import NotificationService, get_notification_service
from app.utils.token import token_services

notification_router = APIRouter(tags=["Notifications"], prefix="/notifications")


@notification_router.get("/", response_model=ListResponse[NotificationDetailResponse])
async def get_notifications(
    data: GetAllNotificationsRequest = Depends(),
    notification_service: NotificationService = Depends(get_notification_service),
    current_user: Annotated[
        UserDetailResponse | None, Depends(token_services.get_data_from_token)
    ] = None,
):
    return await notification_service.get_all_notifications(
        user_id=current_user.id, limit=data.limit, offset=data.offset
    )


@notification_router.put("/{notification_id}", response_model=ResponseModel)
async def mark_read(
    notification_id: int,
    notification_service: NotificationService = Depends(get_notification_service),
    _: Annotated[
        UserDetailResponse | None, Depends(token_services.get_data_from_token)
    ] = None,
):
    await notification_service.mark_read(notification_id=notification_id)
    return ResponseModel(status_code=200, message="Notification marked as read")
