import logging

from fastapi import HTTPException, status

from app.db.unit_of_work import UnitOfWork
from app.utils.password import hash_password
from app.schemas.user import UserSchema, UserUpdateRequestModel

logger = logging.getLogger(__name__)


class UserServices:
    async def create_user(self, user_data: UserSchema):
        try:
            user_data.password = hash_password(user_data.password)

            async with UnitOfWork() as uow:
                user_id = await uow.users.create_user(user_data)
                await uow.commit()

            logger.info(f"User created: {user_data.username}")
            return user_id
        except Exception as e:
            logger.error(f"Error creating user {user_data.username}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create user: {str(e)}",
            )

    async def get_all_users(self):
        try:
            async with UnitOfWork() as uow:
                users = await uow.users.get_all_users()

            logger.info("Fetched all users")
            return users
        except Exception as e:
            logger.error(f"Error fetching all users: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve users: {str(e)}",
            )

    async def get_user_by_id(self, user_id: int):
        try:
            async with UnitOfWork() as uow:
                user = await uow.users.get_user_by_id(user_id)

            if not user:
                logger.warning(f"No user found with id={user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with ID {user_id} not found",
                )

            logger.info(f"Fetched user with id={user_id}")
            return user
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error retrieving user id={user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve user: {str(e)}",
            )

    async def update_user(self, user_id: int, update_data: UserUpdateRequestModel):
        try:
            await self.get_user_by_id(user_id)

            if update_data.password:
                update_data.password = hash_password(update_data.password)
            values_to_update = {}
            for key in update_data.model_fields:
                value = getattr(update_data, key)
                if value:
                    values_to_update[key] = value

            async with UnitOfWork() as uow:
                await uow.users.update_user(user_id, values_to_update)
                await uow.commit()

            logger.info(f"User updated: id={user_id}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating user id={user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to update user: {str(e)}",
            )

    async def delete_user(self, user_id: int):
        try:
            await self.get_user_by_id(user_id)

            async with UnitOfWork() as uow:
                await uow.users.delete_user(user_id)
                await uow.commit()

            logger.info(f"User deleted: id={user_id}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting user id={user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete user: {str(e)}",
            )
