from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, and_

from app.db.repositories.base_repository import BaseRepository
from app.models.membership_model import Memberships
from app.schemas.membership import (
    MembershipDetailResponse,
)


class MembershipRepository(BaseRepository[Memberships, MembershipDetailResponse, None]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Memberships)

    async def delete_membership(self, user_id: int, company_id: int):
        await self.session.execute(
            delete(Memberships).where(
                and_(
                    Memberships.user_id == user_id, Memberships.company_id == company_id
                )
            )
        )
