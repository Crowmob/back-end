import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.base_repository import BaseRepository
from app.models.membership_model import MembershipRequests
from app.models.company_model import Company

logger = logging.getLogger(__name__)


class MembershipRequestsRepository(BaseRepository[MembershipRequests]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, MembershipRequests)

    async def get_membership_requests_for_user(
        self,
        request_type: str,
        user_id: int,
        limit: int | None = None,
        offset: int | None = None,
    ):
        items, total_count = await super().get_all(
            filters={"type": request_type, "user_id": user_id},
            limit=limit,
            offset=offset,
        )
        return items

    async def get_membership_requests_to_company(
        self,
        request_type: str,
        company_id: int,
        limit: int | None = None,
        offset: int | None = None,
    ):
        items, total_count = await super().get_all(
            limit=limit,
            offset=offset,
            joins=[(Company, MembershipRequests.company_id == Company.id)],
            extra_filters=[
                MembershipRequests.type == request_type,
                Company.id == company_id,
            ],
        )
        return items, total_count
