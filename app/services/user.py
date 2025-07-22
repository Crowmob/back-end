import logging
from typing import Optional
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException

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
    async def create_user(username: str, email: str, password: str):
        async with UnitOfWork() as uow:
            password = hash_password(password)
            try:
                user_id = await uow.users.create_user(username, email, password)
                await uow.commit()
                logger.info(f"User created: {username}")
                return user_id
            except IntegrityError:
                await uow.rollback()
                logger.error(
                    f"Error creating user: User with email {email} already exists"
                )
                raise UserAlreadyExistsException(email)

            except SQLAlchemyError as e:
                await uow.rollback()
                logger.error(f"SQLAlchemy error: {e}")
                raise

            except HTTPException as e:
                await uow.rollback()
                logger.error(f"Unexpected error: {e}")
                raise AppException(e.detail, e.status_code)

    @staticmethod
    async def get_all_users(limit: Optional[int] = None, offset: Optional[int] = None):
        async with UnitOfWork() as uow:
            try:
                users = await uow.users.get_all_users(limit, offset)
                logger.info("Fetched users")
                return users

            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise

            except HTTPException as e:
                logger.error(f"Unexpected error: {e}")
                raise AppException(e.detail, e.status_code)

    @staticmethod
    async def get_user_by_id(user_id: int, existing_uow: Optional[UnitOfWork] = None):
        async with UnitOfWork() as uow:
            if existing_uow:
                uow = existing_uow
            try:
                user = await uow.users.get_user_by_id(user_id)
                if not user:
                    logger.warning(f"No user found with id={user_id}")
                    raise UserWithIdNotFoundException(user_id)
                logger.info(f"Fetched user with id={user_id}")
                return user

            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise

            except HTTPException as e:
                logger.error(f"Unexpected error: {e}")
                raise AppException(e.detail, e.status_code)

    @staticmethod
    async def get_user_by_email(email: str, existing_uow: Optional[UnitOfWork] = None):
        async with UnitOfWork() as uow:
            if existing_uow:
                uow = existing_uow
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

            except HTTPException as e:
                logger.error(f"Unexpected error: {e}")
                raise AppException(e.detail, e.status_code)

    async def update_user(self, user_id: int, username: str, email: str, password: str):
        async with UnitOfWork() as uow:
            await self.get_user_by_id(user_id, uow)
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

            except IntegrityError as e:
                await uow.rollback()
                logger.error(f"Integrity error: {e}")
                raise UserUpdateException(user_id)

            except SQLAlchemyError as e:
                await uow.rollback()
                logger.error(f"SQLAlchemy error: {e}")
                raise AppException(detail="Database exception occurred.")

            except HTTPException as e:
                await uow.rollback()
                logger.error(f"Unexpected error: {e}")
                raise AppException(e.detail, e.status_code)

    async def delete_user(self, user_id: int):
        async with UnitOfWork() as uow:
            await self.get_user_by_id(user_id, uow)
            try:
                await uow.users.delete_user(user_id)
                await uow.commit()
                logger.info(f"User deleted: id={user_id}")

            except SQLAlchemyError as e:
                await uow.rollback()
                logger.error(f"SQLAlchemy error: {e}")
                raise

            except HTTPException as e:
                await uow.rollback()
                logger.error(f"Unexpected error: {e}")
                raise AppException(e.detail, e.status_code)
