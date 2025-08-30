from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_, or_

from app.models.company_model import Company
from app.models.membership_model import Memberships
from app.db.repositories.base_repository import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Company)

    async def get_all_companies(
        self,
        limit: int | None = 5,
        offset: int | None = 0,
        current_user: int | None = None,
    ):
        if not current_user:
            items, total_count = await super().get_all(
                filters={"private": False},
                limit=limit,
                offset=offset,
            )
        else:
            query = select(Company, func.count().over().label("total_count"))
            query = (
                query.where(
                    (Company.private == False) | (Company.owner == current_user)
                )
                .offset(offset or 0)
                .limit(limit or 5)
            )
            result = await self.session.execute(query)
            rows = result.all()

            if not rows:
                return [], 0

            total_count = rows[0].total_count
            items = [row[0] for row in rows]
        return items, total_count

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
            return None

        return rows

    async def get_companies_by_ids(self, ids: list[int]):
        if not ids:
            return [], 0
        items, total_count = await super().get_all(
            filters={"id": ids} if ids else {},
            limit=None,
            offset=None,
        )
        return items, total_count

    async def get_company_by_id(self, company_id: int, current_user: int):
        query = (
            select(Company)
            .join(Memberships, Company.id == Memberships.company_id, isouter=True)
            .where(
                and_(
                    Company.id == company_id,
                    or_(
                        Company.private == False,
                        Memberships.user_id == current_user,
                    ),
                )
            )
        )
        result = await self.session.execute(query)
        company = result.scalars().first()
        return company
