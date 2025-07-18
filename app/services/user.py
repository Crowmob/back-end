import logging
from typing import Optional

from app.db.unit_of_work import UnitOfWork
from app.utils.password import hash_password
from app.core.exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    UserUpdateException,
)

logger = logging.getLogger(__name__)


class UserServices:
    @staticmethod
    async def create_user(username: str, email: str, password: str):
        async with UnitOfWork() as uow:
            password = hash_password(password)
            try:
                user_id = await uow.users.create_user(username, email, password)
                await uow.commit()
                logger.info(f"User created: {username}")
                return user_id
            except:
                logger.error(
                    f"Error creating user: User with email {email} already exists"
                )
                raise UserAlreadyExistsException(email)

    @staticmethod
    async def get_all_users(limit: Optional[int] = None, offset: Optional[int] = None):
        async with UnitOfWork() as uow:
            users = await uow.users.get_all_users(limit, offset)
            logger.info("Fetched users")
            return users

    @staticmethod
    async def get_user_by_id(user_id: int):
        async with UnitOfWork() as uow:
            user = await uow.users.get_user_by_id(user_id)
            if not user:
                logger.warning(f"No user found with id={user_id}")
                raise UserNotFoundException(user_id)
            logger.info(f"Fetched user with id={user_id}")
            return user

    async def update_user(self, user_id: int, username: str, email: str, password: str):
        await self.get_user_by_id(user_id)
        async with UnitOfWork() as uow:
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
                await uow.commit()

                logger.info(f"User updated: id={user_id}")
            except:
                logger.error(f"Error updating user id={user_id}: Wrong data")
                raise UserUpdateException(user_id)

    async def delete_user(self, user_id: int):
        await self.get_user_by_id(user_id)
        async with UnitOfWork() as uow:
            await uow.users.delete_user(user_id)
            await uow.commit()
            logger.info(f"User deleted: id={user_id}")
