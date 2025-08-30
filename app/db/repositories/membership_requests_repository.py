from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, delete

from app.db.repositories.base_repository import BaseRepository
from app.models.membership_model import MembershipRequests
from app.models.company_model import Company


class MembershipRequestsRepository(BaseRepository[MembershipRequests]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, MembershipRequests)

    async def get_membership_request(
        self, request_type: str, company_id: int, user_id: int
    ):
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

    async def delete_membership_request(self, user_id: int, company_id: int):
        await self.session.execute(
            delete(MembershipRequests).where(
                and_(
                    MembershipRequests.user_id == user_id,
                    MembershipRequests.company_id == company_id,
                )
            )
        )

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
        query = (
            select(MembershipRequests, func.count().over().label("total_count"))
            .join(
                Company,
                and_(
                    MembershipRequests.company_id == Company.id,
                    Company.id == company_id,
                ),
            )
            .where(MembershipRequests.type == request_type)
            .offset(offset or 0)
            .limit(limit or 5)
        )

        result = await self.session.execute(query)
        rows = result.all()

        if not rows:
            return [], 0

        total_count = rows[0][1]
        items = [row[0] for row in rows]

        return items, total_count
