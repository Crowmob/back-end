import logging

from app.db.unit_of_work import UnitOfWork
from app.utils.password import hash_password
from app.schemas.user import UserUpdateRequestModel, SignUpRequestModel
from app.core.exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    UserUpdateException,
)

logger = logging.getLogger(__name__)


class UserServices:
    async def create_user(self, user_data: SignUpRequestModel):
        user_data.password = hash_password(user_data.password)
        try:
            async with UnitOfWork() as uow:
                user_id = await uow.users.create_user(user_data)
                await uow.commit()

            logger.info(f"User created: {user_data.username}")
            return user_id
        except:
            logger.error(
                f"Error creating user: User with email {user_data.email} already exists"
            )
            raise UserAlreadyExistsException(user_data.email)

    async def get_all_users(self):
        async with UnitOfWork() as uow:
            users = await uow.users.get_all_users()
        logger.info("Fetched all users")
        return users

    async def get_user_by_id(self, user_id: int):
        async with UnitOfWork() as uow:
            user = await uow.users.get_user_by_id(user_id)
        if not user:
            logger.warning(f"No user found with id={user_id}")
            raise UserNotFoundException(user_id)
        logger.info(f"Fetched user with id={user_id}")
        return user

    async def update_user(self, user_id: int, update_data: UserUpdateRequestModel):
        await self.get_user_by_id(user_id)

        if update_data.password:
            update_data.password = hash_password(update_data.password)
        values_to_update = {}
        for key in update_data.model_fields:
            value = getattr(update_data, key)
            if value:
                values_to_update[key] = value
        try:
            async with UnitOfWork() as uow:
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
