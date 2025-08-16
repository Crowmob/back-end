import logging
import os
import glob
import aiofiles

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import UploadFile

from app.db.unit_of_work import UnitOfWork
from app.utils.password import password_services
from app.core.exceptions.user_exceptions import (
    AppException,
    UserWithIdNotFoundException,
    UserWithEmailNotFoundException,
    UserUpdateException,
)
from app.utils.settings_model import settings
from app.schemas.user import UserDetailResponse, UserUpdateRequestModel, UserSchema

logger = logging.getLogger(__name__)


class UserServices:
    @staticmethod
    async def create_user(
        username: str | None,
        email: str,
        password: str | None,
        auth_provider: str | None,
        oauth_id: str | None,
        avatar_ext: str | None = None,
    ):
        async with UnitOfWork() as uow:
            if password:
                password = password_services.hash_password(password)
            try:
                user = UserSchema(
                    username=username,
                    email=email,
                    password=password,
                    avatar_ext=avatar_ext,
                )
                user_id = await uow.users.create(user.model_dump())
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
                logger.info(users)
                return users

            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise

    @staticmethod
    async def get_user_by_id_with_uow(user_id: int, uow: UnitOfWork):
        try:
            user = await uow.users.get_by_id(user_id)
            if not user:
                logger.warning(f"No user found with id={user_id}")
                raise UserWithIdNotFoundException(user_id)
            user_dict = user.__dict__.copy()
            if user_dict["avatar_ext"]:
                user_dict["avatar"] = (
                    f"{settings.BASE_URL}/static/avatars/{user.id}.{user.avatar_ext}"
                )
            user_dict.pop("avatar_ext")
            logger.info(f"Fetched user with id={user_id}")
            return UserDetailResponse.model_validate(user_dict)

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

    async def update_user(
        self,
        user_id: int,
        username: str | None = None,
        password: str | None = None,
        about: str | None = None,
        avatar: UploadFile | None = None,
    ):
        async with UnitOfWork() as uow:
            user = await self.get_user_by_id_with_uow(user_id, uow)
            if avatar:
                ext = avatar.filename.split(".")[-1]
                filename = f"{user_id}.{ext}"
                filepath = os.path.join("static/avatars/", filename)
                pattern = f"/static/avatars/{user_id}.*"
                matches = glob.glob(pattern)
                if matches:
                    for file_path in matches:
                        os.remove(file_path)
                async with aiofiles.open(filepath, "wb") as out_file:
                    while content := await avatar.read(1024):
                        await out_file.write(content)
            else:
                ext = None
            if password:
                password = password_services.hash_password(password)
            try:
                update_model = UserUpdateRequestModel(
                    username=username,
                    password=password,
                    about=about,
                    avatar_ext=ext if ext else user.avatar,
                )
                await uow.users.update(
                    user_id,
                    update_model.model_dump(),
                )

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
