import logging

from app.core.enums.enums import NotificationStatus
from app.core.exceptions.exceptions import (
    AppException,
    NotFoundException,
    BadRequestException,
)
from app.core.exceptions.repository_exceptions import (
    RepositoryDatabaseError,
    RepositoryIntegrityError,
    RepositoryDataError,
)
from app.db.unit_of_work import UnitOfWork
from app.schemas.notification import NotificationDetailResponse
from app.schemas.response_models import ListResponse

logger = logging.getLogger(__name__)


class NotificationService:
    @staticmethod
    async def get_all_notifications(
        user_id: int, limit: int | None, offset: int | None
    ):
        async with UnitOfWork() as uow:
            try:
                items, total_count = await uow.notifications.get_all_notifications(
                    user_id=user_id, limit=limit, offset=offset
                )
                notifications = [
                    NotificationDetailResponse(
                        id=notification.id,
                        status=notification.status,
                        created_at=notification.created_at,
                        message=notification.message,
                    )
                    for notification in items
                ]
                return ListResponse[NotificationDetailResponse](
                    items=notifications, count=total_count
                )
            except RepositoryDatabaseError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise AppException("Database exception occurred")

    @staticmethod
    async def mark_read(notification_id: int):
        async with UnitOfWork() as uow:
            try:
                notification = await uow.notifications.get_one(id=notification_id)
            except RepositoryDatabaseError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise AppException("Database exception occurred")
            if not notification:
                raise NotFoundException("Notification not found")
            try:
                await uow.notifications.update(
                    data={"status": NotificationStatus.READ}, id=notification_id
                )
            except RepositoryIntegrityError as e:
                logger.error(f"IntegrityError: {e}")
                raise BadRequestException(
                    detail="Failed to mark read notification. Wrong data"
                )
            except RepositoryDataError as e:
                logger.error(f"Data error: {e}")
                raise BadRequestException(detail="Invalid format or length of fields")
            except RepositoryDatabaseError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise AppException(detail="Database exception occurred.")


def get_notification_service() -> NotificationService:
    return NotificationService()
