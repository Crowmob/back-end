from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete, func

from app.models.company_model import Company
from app.models.membership_model import Memberships
from app.schemas.company import (
    CompanyDetailResponse,
    CompanySchema,
    CompanyUpdateRequestModel,
)
from app.schemas.response_models import ListResponse
from app.db.repositories.base_repository import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Company)

    async def get_all_companies(self, limit: int | None = 5, offset: int | None = 0):
        query = (
            select(Company, func.count().over().label("total_count"))
            .offset(offset or 0)
            .limit(limit or 10)
        )

        result = await self.session.execute(query)
        rows = result.all()

        if not rows:
            return ListResponse[CompanyDetailResponse](items=[], count=0)

        total_count = rows[0].total_count

        items = [
            CompanyDetailResponse(
                id=row.id,
                owner=row.owner,
                name=row.name,
                description=row.description,
                private=row.private,
            )
            for row, _ in rows
        ]

        return ListResponse[CompanyDetailResponse](items=items, count=total_count)

    async def get_companies_for_user(
        self, user_id: int, limit: int | None = None, offset: int | None = None
    ):
        query = (
            select(Company, Memberships.role, func.count().over().label("total_count"))
            .join(Memberships, Company.id == Memberships.company_id)
            .filter(Memberships.user_id == user_id)
            .limit(limit or 5)
            .offset(offset or 0)
        )

        result = await self.session.execute(query)
        rows = result.all()

        if not rows:
            return ListResponse[CompanyDetailResponse](items=[], count=0)

        total_count = rows[0][2]

        items = [
            CompanyDetailResponse(
                id=company.id,
                owner=company.owner,
                name=company.name,
                description=company.description,
                private=company.private,
                user_role=role,
            )
            for company, role, _ in rows
        ]

        return ListResponse[CompanyDetailResponse](items=items, count=total_count)

    async def get_companies_by_ids(self, ids: list):
        if not ids:
            return ListResponse[CompanyDetailResponse](items=[], count=0)
        query = select(Company, func.count().over().label("total_count")).where(
            Company.id.in_(ids)
        )

        result = await self.session.execute(query)
        rows = result.all()

        total_count = rows[0][1]

        items = [
            CompanyDetailResponse(
                id=company.id,
                owner=company.owner,
                name=company.name,
                description=company.description,
                private=company.private,
            )
            for company, _ in rows
        ]
        return ListResponse[CompanyDetailResponse](items=items, count=total_count)
