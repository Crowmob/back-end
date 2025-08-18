from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, delete

from app.db.repositories.base_repository import BaseRepository
from app.models.membership_model import MembershipRequests
from app.schemas.membership import MembershipRequestDetailResponse
from app.schemas.response_models import ListResponse
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
                and_(user_id == user_id, company_id == company_id)
            )
        )

    async def get_membership_requests_for_user(
        self,
        request_type: str,
        user_id: int,
        limit: int | None = None,
        offset: int | None = None,
    ):
        query = (
            select(MembershipRequests, func.count().over().label("total_count"))
            .where(
                and_(
                    MembershipRequests.type == request_type,
                    MembershipRequests.user_id == user_id,
                )
            )
            .offset(offset or 0)
            .limit(limit or 5)
        )

        result = await self.session.execute(query)
        rows = result.all()

        if not rows:
            return ListResponse[MembershipRequestDetailResponse](items=[], count=0)

        total_count = rows[0][1]
        items = [
            MembershipRequestDetailResponse(
                id=request.id,
                type=request.type,
                company_id=request.company_id,
                user_id=request.user_id,
            )
            for request, _ in rows
        ]
        return ListResponse[MembershipRequestDetailResponse](
            items=items, count=total_count
        )

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
            return ListResponse[MembershipRequestDetailResponse](items=[], count=0)

        total_count = rows[0][1]
        items = [
            MembershipRequestDetailResponse(
                id=req.id, type=req.type, company_id=req.company_id, user_id=req.user_id
            )
            for req, _ in rows
        ]

        return ListResponse[MembershipRequestDetailResponse](
            items=items, count=total_count
        )
