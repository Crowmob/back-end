import logging

from sqlalchemy.exc import SQLAlchemyError

from app.db.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


class AdminServices:
    @staticmethod
    async def appoint_admin(user_id: int, company_id: int):
        async with UnitOfWork() as uow:
            try:
                await uow.memberships.appoint_admin(user_id, company_id)
                logger.info(f"Appointed admin with id {user_id}")
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise

    @staticmethod
    async def remove_admin(user_id: int, company_id: int):
        async with UnitOfWork() as uow:
            try:
                await uow.memberships.remove_admin(user_id, company_id)
                logger.info(f"Removed admin with id {user_id}")
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise

    @staticmethod
    async def get_all_admins(
        company_id: int, limit: int | None = None, offset: int | None = None
    ):
        async with UnitOfWork() as uow:
            try:
                return await uow.users.get_all_admins(company_id, limit, offset)
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise


admin_services = AdminServices()
