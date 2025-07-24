import logging
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.db.unit_of_work import UnitOfWork
from app.utils.password import hash_password
from app.core.exceptions.user_exceptions import (
    AppException,
    UserWithIdNotFoundException,
    UserWithEmailNotFoundException,
    UserAlreadyExistsException,
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
    ):
        async with UnitOfWork() as uow:
            if password:
                password = hash_password(password)
            try:
                user_id = await uow.users.create_user(
                    username, email, password, auth_provider, oauth_id
                )
                logger.info(f"User created: {username}")
                return user_id
            except IntegrityError:
                logger.error(
                    f"Error creating user: User with email {email} already exists"
                )
                raise UserAlreadyExistsException(email)

            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise

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
    async def get_user_by_id_with_uow(user_id: int, uow: UnitOfWork):
        try:
            user = await uow.users.get_user_by_id(user_id)
            if not user:
                logger.warning(f"No user found with id={user_id}")
                raise UserWithIdNotFoundException(user_id)
            logger.info(f"Fetched user with id={user_id}")
            return user

        except SQLAlchemyError as e:
            logger.info(f"SQLAlchemy error: {e}")
            raise

    async def get_user_by_id(self, user_id: int):
        async with UnitOfWork() as uow:
            return await self.get_user_by_id_with_uow(user_id, uow)

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

    async def update_user(self, user_id: int, username: str, email: str, password: str):
        async with UnitOfWork() as uow:
            await self.get_user_by_id_with_uow(user_id, uow)
            if password:
                password = hash_password(password)
            values_to_update = {
                "username": username,
                "email": email,
                "password": password,
            }
            for key in list(values_to_update.keys()):
                if values_to_update[key] is None:
                    values_to_update.pop(key)
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
