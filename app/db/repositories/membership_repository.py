from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, and_, update, select

from app.core.enums.role_enum import RoleEnum
from app.db.repositories.base_repository import BaseRepository
from app.models.membership_model import Memberships
from app.schemas.membership import MembershipDetailResponse


class MembershipRepository(BaseRepository[Memberships]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Memberships)

    async def get_membership(self, user_id: int, company_id: int):
        result = await self.session.execute(
            select(Memberships).where(
                and_(
                    Memberships.user_id == user_id, Memberships.company_id == company_id
                )
            )
        )
        row = result.scalar_one_or_none()
        if not row:
            return None
        return MembershipDetailResponse.model_validate(row)

    async def delete_membership(self, user_id: int, company_id: int):
        await self.session.execute(
            delete(Memberships).where(
                and_(
                    Memberships.user_id == user_id, Memberships.company_id == company_id
                )
            )
        )

    async def appoint_admin(self, user_id: int, company_id: int):
        await self.session.execute(
            update(Memberships)
            .values(role=RoleEnum.ADMIN)
            .where(
                and_(
                    Memberships.user_id == user_id, Memberships.company_id == company_id
                )
            )
        )

    async def remove_admin(self, user_id: int, company_id: int):
        await self.session.execute(
            update(Memberships)
            .values(role=RoleEnum.MEMBER)
            .where(
                and_(
                    Memberships.user_id == user_id, Memberships.company_id == company_id
                )
            )
        )
