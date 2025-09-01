from typing import Annotated

from fastapi import APIRouter, Depends, Form, UploadFile, File

from app.services.user import get_user_service, UserServices
from app.utils.token import token_services
from app.schemas.user import (
    GetAllUsersRequestModel,
    SignUpRequestModel,
    UserDetailResponse,
    UserSchema,
)
from app.schemas.response_models import ResponseModel, ListResponse

user_router = APIRouter(tags=["User CRUD"], prefix="/users")


@user_router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user_by_id_endpoint(
    user_id: int,
    current_user: Annotated[
        UserDetailResponse | None, Depends(token_services.get_data_from_token)
    ],
    user_service: UserServices = Depends(get_user_service),
):
    return await user_service.get_user_by_id(user_id, current_user.email)


@user_router.get("/", response_model=ListResponse[UserDetailResponse])
async def get_all_users_endpoint(
    data: GetAllUsersRequestModel = Depends(),
    user_service: UserServices = Depends(get_user_service),
):
    return await user_service.get_all_users(data.limit, data.offset)


@user_router.post("/", response_model=ResponseModel)
async def create_user_endpoint(
    data: SignUpRequestModel, user_service: UserServices = Depends(get_user_service)
):
    user_id = await user_service.create_user(
        data.username, data.email, data.password, data.avatar
    )
    return ResponseModel(
        status_code=200, message=f"Created user successfully! id: {user_id}"
    )


@user_router.put("/{user_id}", response_model=ResponseModel)
async def update_user_endpoint(
    user_id: int,
    username: str = Form(...),
    about: str = Form(...),
    avatar: UploadFile = File(None),
    user_service: UserServices = Depends(get_user_service),
    current_user: Annotated[
        UserDetailResponse | None, Depends(token_services.get_data_from_token)
    ] = None,
):
    await user_service.update_user(
        user_id, username, about=about, avatar=avatar, current_user=current_user
    )
    return ResponseModel(
        status_code=200, message=f"Successfully updated user with id: {user_id}!"
    )


@user_router.delete("/{user_id}", response_model=ResponseModel)
async def delete_user_endpoint(
    user_id: int,
    user_service: UserServices = Depends(get_user_service),
    current_user: Annotated[
        UserDetailResponse | None, Depends(token_services.get_data_from_token)
    ] = None,
):
    await user_service.delete_user(user_id, current_user)
    return ResponseModel(
        status_code=200, message=f"Successfully deleted user with id: {user_id}!"
    )
