import pytest
from sqlalchemy import select

from app.core.enums.enums import NotificationStatus
from app.models.notifications_model import Notification


@pytest.mark.asyncio
async def test_get_all_notifications(
    db_session, notification_services_fixture, test_notification
):
    notifications = await notification_services_fixture.get_all_notifications(
        user_id=test_notification["user_id"], limit=5, offset=0
    )
    assert notifications.count >= 1


@pytest.mark.asyncio
async def test_mark_read(db_session, notification_services_fixture, test_notification):
    await notification_services_fixture.mark_read(test_notification["id"])

    notification = await db_session.scalar(
        select(Notification).where(Notification.id == test_notification["id"])
    )
    assert notification.status == NotificationStatus.READ
