from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete, func

from app.models.company_model import Company
from app.schemas.company import CompanyDetailResponse, ListResponse


class CompanyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_company(
        self, owner: int, name: str, description: str, private: bool = False
    ):
        new_company = Company(
            owner=owner, name=name, description=description, private=private
        )
        self.session.add(new_company)

    async def get_all_companies(self, limit: int | None = 5, offset: int | None = 0):
        stmt = (
            select(Company, func.count().over().label("total_count"))
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        if not rows:
            return ListResponse[CompanyDetailResponse](items=[], count=0)

        total_count = rows[0][1]

        items = [
            CompanyDetailResponse(
                id=company.id,
                name=company.name,
                description=company.description,
                private=company.private,
            )
            for company, _ in rows
        ]

        return ListResponse[CompanyDetailResponse](items=items, count=total_count)

    async def get_company_by_id(self, company_id: int):
        result = await self.session.execute(
            select(Company).where(Company.id == company_id)
        )
        company = result.scalar_one_or_none()
        if not company:
            return None
        return CompanyDetailResponse.model_validate(company)

    async def update_company(self, company_id: int, values_to_update):
        await self.session.execute(
            update(Company).where(Company.id == company_id).values(**values_to_update)
        )

    async def delete_company(self, company_id: int):
        await self.session.execute(delete(Company).where(Company.id == company_id))
