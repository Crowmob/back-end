import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, delete

from app.core.exceptions.exceptions import AppException
from app.db.repositories.base_repository import BaseRepository
from app.models.membership_model import MembershipRequests
from app.models.company_model import Company

logger = logging.getLogger(__name__)


class MembershipRequestsRepository(BaseRepository[MembershipRequests]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, MembershipRequests)

    async def get_membership_request(
        self, request_type: str, company_id: int, user_id: int
    ):
        try:
            result = await self.session.execute(
                select(MembershipRequests).where(
                    and_(
                        MembershipRequests.type == request_type,
                        MembershipRequests.user_id == user_id,
                        MembershipRequests.company_id == company_id,
                    )
                )
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError: {e}")
            raise AppException(detail="Database exception occurred.")

    async def delete_membership_request(self, user_id: int, company_id: int):
        try:
            await self.session.execute(
                delete(MembershipRequests).where(
                    and_(
                        MembershipRequests.user_id == user_id,
                        MembershipRequests.company_id == company_id,
                    )
                )
            )
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError: {e}")
            raise AppException(detail="Database exception occurred.")

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
