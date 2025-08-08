from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select, and_, func

from app.models.membership_model import MembershipRequests, Memberships
from app.models.company_model import Company
from app.schemas.membership import (
    MembershipRequestDetailResponse,
    MembershipDetailResponse,
)
from app.schemas.response_models import ListResponse


class MembershipRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_membership_request(
        self, request_type: str, from_id: int, to_id: int
    ):
        membership_request = MembershipRequests(
            type=request_type, from_id=from_id, to_id=to_id
        )
        self.session.add(membership_request)
        await self.session.flush()
        await self.session.refresh(membership_request)
        return membership_request.id

    async def get_membership_request_by_id(self, request_id: int):
        result = await self.session.execute(
            select(MembershipRequests).where(MembershipRequests.id == request_id)
        )
        membership_request = result.scalar_one_or_none()
        if not membership_request:
            return None
        return MembershipRequestDetailResponse.model_validate(membership_request)

    async def delete_membership_request(self, request_id: int):
        await self.session.execute(
            delete(MembershipRequests).where(MembershipRequests.id == request_id)
        )

    async def create_membership(self, user_id: int, company_id: int):
        membership = Memberships(user_id=user_id, company_id=company_id)
        self.session.add(membership)
        await self.session.flush()
        await self.session.refresh(membership)
        return membership.id

    async def delete_membership(self, user_id: int, company_id: int):
        await self.session.execute(
            delete(Memberships).where(
                and_(
                    Memberships.user_id == user_id, Memberships.company_id == company_id
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

    async def get_membership_requests_for_owner(
        self,
        owner_id: int,
        request_type: str,
        limit: int | None = None,
        offset: int | None = None,
    ):
        stmt = (
            select(MembershipRequests, func.count().over().label("total_count"))
            .join(
                Company,
                Company.id
                == (
                    MembershipRequests.to_id
                    if request_type == "request"
                    else MembershipRequests.from_id
                ),
            )
            .where(
                and_(Company.owner == owner_id, MembershipRequests.type == request_type)
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
                id=req.id, type=req.type, from_id=req.from_id, to_id=req.to_id
            )
            for req, _ in rows
        ]

        return ListResponse[MembershipRequestDetailResponse](
            items=items, count=total_count
        )

    async def get_all_memberships(
        self, company_id: int, limit: int | None = None, offset: int | None = None
    ):
        stmt = (
            select(Memberships, func.count().over().label("total_count"))
            .where(Memberships.company_id == company_id)
            .offset(offset or 0)
            .limit(limit or 5)
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        if not rows:
            return ListResponse[MembershipDetailResponse](items=[], count=0)

        total_count = rows[0][1]
        items = [
            MembershipDetailResponse(
                id=request.id, user_id=request.user_id, company_id=request.company_id
            )
            for request, _ in rows
        ]
        return ListResponse[MembershipDetailResponse](items=items, count=total_count)
