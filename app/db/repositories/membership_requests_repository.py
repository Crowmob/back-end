from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.db.repositories.base_repository import BaseRepository
from app.models.membership_model import MembershipRequests
from app.schemas.membership import MembershipRequestDetailResponse
from app.schemas.response_models import ListResponse
from app.models.company_model import Company


class MembershipRequestsRepository(
    BaseRepository[MembershipRequests, MembershipRequestDetailResponse, None]
):
    def __init__(self, session: AsyncSession):
        super().__init__(session, MembershipRequests)

    async def get_membership_request(
        self, request_type: str, user_id: int, company_id: int
    ):
        query = select(MembershipRequests)

        if request_type == "request":
            query = query.where(
                and_(
                    MembershipRequests.type == request_type,
                    MembershipRequests.from_id == user_id,
                    MembershipRequests.to_id == company_id,
                )
            )
        elif request_type == "invite":
            query = query.where(
                and_(
                    MembershipRequests.type == request_type,
                    MembershipRequests.from_id == company_id,
                    MembershipRequests.to_id == user_id,
                )
            )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_membership_requests_for_user(
        self,
        request_type: str,
        user_id: int,
        limit: int | None = None,
        offset: int | None = None,
    ):
        stmt = (
            select(MembershipRequests, func.count().over().label("total_count"))
            .where(
                and_(
                    MembershipRequests.type == request_type,
                    (
                        MembershipRequests.from_id
                        if request_type == "request"
                        else MembershipRequests.to_id
                    )
                    == user_id,
                )
            )
            .offset(offset or 0)
            .limit(limit or 5)
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        if not rows:
            return ListResponse[MembershipRequestDetailResponse](items=[], count=0)

        total_count = rows[0][1]
        items = [
            MembershipRequestDetailResponse(
                id=request.id,
                type=request.type,
                from_id=request.from_id,
                to_id=request.to_id,
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
        if request_type == "request":
            join_condition = and_(
                MembershipRequests.to_id == Company.id, Company.id == company_id
            )
        else:
            join_condition = and_(
                MembershipRequests.from_id == Company.id, Company.id == company_id
            )

        stmt = (
            select(MembershipRequests, func.count().over().label("total_count"))
            .join(Company, join_condition)
            .where(MembershipRequests.type == request_type)
            .offset(offset or 0)
            .limit(limit or 5)
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        if not rows:
            return ListResponse[MembershipRequestDetailResponse](items=[], count=0)

        total_count = rows[0][1]
        items = [
            MembershipRequestDetailResponse(
                id=req.id, type=req.type, from_id=req.from_id, to_id=req.to_id
            )
            for req, _ in rows
        ]

        return ListResponse[MembershipRequestDetailResponse](
            items=items, count=total_count
        )
