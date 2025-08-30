import logging

from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions.exceptions import AppException
from app.db.unit_of_work import UnitOfWork
from app.schemas.response_models import ListResponse, ResponseModel
from app.schemas.user import MemberDetailResponse
from app.utils.settings_model import settings

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
                raise AppException("Database exception occurred.")

    @staticmethod
    async def get_all_admins(
        company_id: int, limit: int | None = None, offset: int | None = None
    ):
        async with UnitOfWork() as uow:
            try:
                result = await uow.users.get_all_admins(company_id, limit, offset)
                if not result:
                    return ListResponse[MemberDetailResponse](items=[], count=0)

                total_count = result[0][2]
                items = [
                    MemberDetailResponse(
                        id=user.id,
                        username=user.username,
                        email=user.email,
                        about=user.about,
                        role=role,
                        avatar=f"{settings.BASE_URL}/static/avatars/{user.id}.{user.avatar_ext}"
                        if user.avatar_ext
                        else None,
                    )
                    for user, role, _ in result
                ]
                return ListResponse[MemberDetailResponse](
                    items=items, count=total_count
                )
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise AppException("Database exception occurred.")


def get_admin_service() -> AdminServices:
    return AdminServices()
