from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_, or_

from app.models.company_model import Company
from app.models.membership_model import Memberships
from app.db.repositories.base_repository import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Company)

    async def get_all_companies_for_owner(self, limit=5, offset=0, current_user=None):
        items, total = await super().get_all(
            limit=limit,
            offset=offset,
            extra_filters=[
                or_(Company.private == False, Company.owner == current_user)
            ],
        )
        return items, total

    async def get_companies_for_user(self, user_id, limit=None, offset=None):
        items, total = await super().get_all(
            limit=limit,
            offset=offset,
            joins=[(Memberships, Company.id == Memberships.company_id)],
            extra_filters=[Memberships.user_id == user_id],
            extra_columns=[Memberships.role],
        )
        return items, total

    async def get_companies_by_ids(self, ids: list[int]):
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
