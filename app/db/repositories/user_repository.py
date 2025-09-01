import logging

from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, func, and_, Select

from app.core.enums.enums import RoleEnum
from app.core.exceptions.exceptions import AppException, BadRequestException
from app.models.user_model import User
from app.models.membership_model import Memberships
from app.db.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_all_users(self, limit: int | None = None, offset: int | None = None):
        items, total_count = await super().get_all(
            filters={"has_profile": True},
            limit=limit,
            offset=offset,
        )
        return items, total_count

    async def get_user_by_email(self, email: int):
        try:
            result = await self.session.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            if user:
                return user
            return None
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError: {e}")
            raise AppException(detail="Database exception occurred.")

    async def delete_user(self, user_id: int) -> None:
        try:
            await self.session.execute(
                update(User)
                .where(User.id == user_id)
                .values(**{"about": None, "has_profile": False})
            )
        except IntegrityError as e:
            logger.error(f"IntegrityError: {e}")
            raise BadRequestException(detail="Failed to update. Wrong data")
        except DataError as e:
            logger.error(f"Data error: {e}")
            raise BadRequestException(detail="Invalid format or length of fields")
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError: {e}")
            raise AppException(detail="Database exception occurred.")

    async def get_users_in_company(
        self, company_id: int, limit: int | None = None, offset: int | None = None
    ):
        items, total_count = await super().get_all(
            limit=limit,
            offset=offset,
            joins=[(Memberships, User.id == Memberships.user_id)],
            extra_filters=[Memberships.company_id == company_id],
            extra_columns=[Memberships.role],
        )

        return items, total_count

    async def get_users_by_ids(self, ids: list[int]):
        items, total_count = await super().get_all(
            filters={"id": ids} if ids else {},
            limit=None,
            offset=None,
        )

        return items, total_count

    async def get_all_admins(self, company_id: int, limit=None, offset=None):
        items, total = await super().get_all(
            limit=limit,
            offset=offset,
            joins=[(Memberships, User.id == Memberships.user_id)],
            extra_filters=[
                Memberships.company_id == company_id,
                Memberships.role == RoleEnum.ADMIN,
            ],
            extra_columns=[Memberships.role],
        )

        return items, total
