from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.base_repository import BaseRepository
from app.models.membership_model import Memberships
from app.models.notifications_model import Notification


class NotificationsRepository(BaseRepository[Notification]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Notification)

    async def get_all_notifications(
        self, user_id: int, limit: int | None, offset: int | None
    ):
        items, total_count = await self.get_all(
            limit=limit,
            offset=offset,
            joins=[(Memberships, Memberships.company_id == Notification.company_id)],
            extra_filters=[Memberships.user_id == user_id],
        )
        return items, total_count
