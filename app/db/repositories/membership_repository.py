import logging

from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, and_, update, select

from app.core.enums.enums import RoleEnum
from app.core.exceptions.exceptions import AppException, BadRequestException
from app.db.repositories.base_repository import BaseRepository
from app.models.membership_model import Memberships

logger = logging.getLogger(__name__)


class MembershipRepository(BaseRepository[Memberships]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Memberships)

    async def get_membership(self, user_id: int, company_id: int):
        try:
            result = await self.session.execute(
                select(Memberships).where(
                    and_(
                        Memberships.user_id == user_id,
                        Memberships.company_id == company_id,
                    )
                )
            )
            row = result.scalar_one_or_none()
            if not row:
                return None
            return row
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError in get_all: {e}")
            raise AppException("Database exception occurred.")

    async def delete_membership(self, user_id: int, company_id: int):
        try:
            await self.session.execute(
                delete(Memberships).where(
                    and_(
                        Memberships.user_id == user_id,
                        Memberships.company_id == company_id,
                    )
                )
            )
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError in get_all: {e}")
            raise AppException("Database exception occurred.")

    async def appoint_admin(self, user_id: int, company_id: int):
        try:
            result = await self.session.execute(
                update(Memberships)
                .values(role=RoleEnum.ADMIN)
                .where(
                    and_(
                        Memberships.user_id == user_id,
                        Memberships.company_id == company_id,
                    )
                )
            )
            return result
        except IntegrityError as e:
            logger.error(f"IntegrityError: {e}")
            raise BadRequestException(detail="Failed to update. Wrong data")
        except DataError as e:
            logger.error(f"Data error: {e}")
            raise BadRequestException(detail="Invalid format or length of fields")
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError in get_all: {e}")
            raise AppException("Database exception occurred.")

    async def remove_admin(self, user_id: int, company_id: int):
        try:
            result = await self.session.execute(
                update(Memberships)
                .values(role=RoleEnum.MEMBER)
                .where(
                    and_(
                        Memberships.user_id == user_id,
                        Memberships.company_id == company_id,
                    )
                )
            )
            return result
        except IntegrityError as e:
            logger.error(f"IntegrityError: {e}")
            raise BadRequestException(detail="Failed to update. Wrong data")
        except DataError as e:
            logger.error(f"Data error: {e}")
            raise BadRequestException(detail="Invalid format or length of fields")
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError in get_all: {e}")
            raise AppException("Database exception occurred.")
