import logging
import os
import glob
import aiofiles

from sqlalchemy.exc import IntegrityError, SQLAlchemyError, DataError
from fastapi import UploadFile

from app.db.unit_of_work import UnitOfWork
from app.schemas.response_models import ListResponse
from app.utils.password import password_services
from app.core.exceptions.exceptions import (
    AppException,
    NotFoundException,
    ConflictException,
    BadRequestException,
    UnauthorizedException,
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
                return user_id
            except IntegrityError:
                logger.warning(f"User with email {email} already exists.")
                raise ConflictException(
                    detail=f"User with email {email} already exists."
                )
            except DataError:
                logger.error(f"Data Error: {e}")
                raise BadRequestException(detail=f"invalid format or length of fields")
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise AppException(detail="Database exception occurred")

    @staticmethod
    async def get_all_users(limit: int | None = None, offset: int | None = None):
        async with UnitOfWork() as uow:
            try:
                items, total_count = await uow.users.get_all_users(limit, offset)
                return ListResponse[UserDetailResponse](
                    items=[
                        UserDetailResponse(
                            id=user.id,
                            username=user.username,
                            email=user.email,
                            about=user.about,
                            avatar=(
                                f"{settings.BASE_URL}/static/avatars/{user.id}.{user.avatar_ext}"
                                if user.avatar_ext
                                else None
                            ),
                        )
                        for user in items
                    ],
                    count=total_count,
                )

            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise AppException(detail="Database exception occurred.")

    @staticmethod
    async def get_user_by_id_with_uow(user_id: int, uow: UnitOfWork):
        try:
            user = await uow.users.get_by_id(user_id)
            if not user:
                logger.warning(f"No user found with id={user_id}")
                raise NotFoundException(detail=f"No user found with id={user_id}")
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
            raise AppException(detail="Database exception occurred.")

    async def get_user_by_id(self, user_id: int, email: str | None):
        async with UnitOfWork() as uow:
            if not email:
                raise UnauthorizedException(detail="Unauthorized")
            user_data = await self.get_user_by_id_with_uow(user_id, uow)
            if email == user_data.email:
                user_data.current_user = True
            return user_data

    @staticmethod
    async def get_user_by_email(email: str):
        async with UnitOfWork() as uow:
            try:
                user = await uow.users.get_user_by_email(email)
                if not user:
                    logger.warning(f"No user found with email={email}")
                    raise NotFoundException(detail=f"No user found with email={email}")
                logger.info(f"Fetched user with email={email}")
                return UserDetailResponse.model_validate(user)

            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise AppException(detail="Database exception occurred.")

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
                    avatar_ext=ext
                    if ext
                    else (user.avatar.split(".")[-1] if user.avatar else None),
                )
                await uow.users.update(
                    user_id,
                    update_model.model_dump(),
                )

                logger.info(f"User updated: id={user_id}")

            except IntegrityError as e:
                logger.error(f"Integrity error: {e}")
                raise BadRequestException(detail="Error updating user. Wrong data")
            except DataError as e:
                logger.error(f"Data error: {e}")
                raise BadRequestException(detail="Invalid format or length of fields")
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
                raise AppException(detail="Database exception occurred.")


def get_user_service() -> UserServices:
    return UserServices()
