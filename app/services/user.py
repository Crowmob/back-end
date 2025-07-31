import logging
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.db.unit_of_work import UnitOfWork
from app.utils.password import password_services
from app.core.exceptions.user_exceptions import (
    AppException,
    UserWithIdNotFoundException,
    UserWithEmailNotFoundException,
    UserUpdateException,
)

logger = logging.getLogger(__name__)


class UserServices:
    @staticmethod
    async def create_user(
        username: str | None,
        email: str,
        password: str | None,
        auth_provider: str | None,
        oauth_id: str | None,
        avatar: bytes | None = None,
    ):
        async with UnitOfWork() as uow:
            if password:
                password = password_services.hash_password(password)

            try:
                logger.info(avatar)
                user_id = await uow.users.create_user(
                    username=username, email=email, password=password, avatar=avatar
                )
                logger.info(f"User created: {username}")

            except IntegrityError:
                logger.warning(f"User with email {email} already exists.")
                await uow.session.rollback()

                user = await uow.users.get_user_by_email(email)
                if not user:
                    logger.error(f"User not found by email: {email}")
                    raise UserWithEmailNotFoundException(email=email)

                user_id = user.id

            if auth_provider and oauth_id:
                exists = await uow.users.identity_exists(oauth_id)
                if exists:
                    logger.warning(
                        f"Identity for provider {auth_provider} already exists."
                    )
                else:
                    await uow.users.create_identity(
                        user_id=user_id,
                        provider=auth_provider,
                        provider_id=oauth_id,
                    )
                    logger.info(f"Created identity for provider {auth_provider}")

            return user_id

    @staticmethod
    async def get_all_users(limit: int | None = None, offset: int | None = None):
        async with UnitOfWork() as uow:
            try:
                users = await uow.users.get_all_users(limit, offset)
                logger.info("Fetched users")
                return users

            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise

    @staticmethod
    async def get_user_by_id_with_uow(
        user_id: int, uow: UnitOfWork, get_avatar: bool = False
    ):
        try:
            user = await uow.users.get_user_by_id(user_id, get_avatar)
            if not user:
                logger.warning(f"No user found with id={user_id}")
                raise UserWithIdNotFoundException(user_id)
            logger.info(f"Fetched user with id={user_id}")
            return user

        except SQLAlchemyError as e:
            logger.info(f"SQLAlchemy error: {e}")
            raise

    async def get_user_by_id(self, user_id: int, get_avatar: bool = False):
        async with UnitOfWork() as uow:
            return await self.get_user_by_id_with_uow(user_id, uow, get_avatar)

    @staticmethod
    async def get_user_by_email(email: str):
        async with UnitOfWork() as uow:
            try:
                user = await uow.users.get_user_by_email(email)
                if not user:
                    logger.warning(f"No user found with email={email}")
                    raise UserWithEmailNotFoundException(email)
                logger.info(f"Fetched user with email={email}")
                return user

            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise

    async def update_user(
        self,
        user_id: int,
        username: str | None = None,
        password: str | None = None,
        about: str | None = None,
        avatar: bytes | None = None,
    ):
        async with UnitOfWork() as uow:
            await self.get_user_by_id_with_uow(user_id, uow)
            if password:
                password = password_services.hash_password(password)
            values_to_update = {
                "username": username,
                "password": password,
                "about": about,
                "avatar": avatar,
            }
            for key in list(values_to_update.keys()):
                if values_to_update[key] is None:
                    values_to_update.pop(key)
            logger.info(values_to_update)
            try:
                await uow.users.update_user(user_id, values_to_update)

                logger.info(f"User updated: id={user_id}")

            except IntegrityError as e:
                logger.error(f"Integrity error: {e}")
                raise UserUpdateException(user_id)

            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise AppException(detail="Database exception occurred.")

    async def delete_user(self, user_id: int):
        async with UnitOfWork() as uow:
            await self.get_user_by_id_with_uow(user_id, uow)
            try:
                await uow.users.delete_user(user_id)
                logger.info(f"User deleted: id={user_id}")

            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise


user_services = UserServices()
