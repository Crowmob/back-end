from typing import Annotated

from fastapi import APIRouter, Depends, Header, Form, UploadFile, File

from app.services.user import user_services
from app.utils.token import token_services
from app.schemas.user import (
    GetAllUsersRequestModel,
    SignUpRequestModel,
    UserDetailResponse,
)
from app.schemas.response_models import ResponseModel, ListResponse

user_router = APIRouter(tags=["User CRUD"], prefix="/users")


@user_router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user_by_id_endpoint(
    user_id: int,
    email: Annotated[str | None, Depends(token_services.get_data_from_token)],
):
    user_data = await user_services.get_user_by_id(user_id)
    if email == user_data.email:
        user_data.current_user = True
    return user_data


@user_router.get("/{email}", response_model=UserDetailResponse)
async def get_user_by_email_endpoint(email: str):
    return await user_services.get_user_by_email(email)


@user_router.get("/", response_model=ListResponse[UserDetailResponse])
async def get_all_users_endpoint(data: GetAllUsersRequestModel = Depends()):
    return await user_services.get_all_users(data.limit, data.offset)


@user_router.post("/", response_model=ResponseModel)
async def create_user_endpoint(data: SignUpRequestModel):
    user_id = await user_services.create_user(
        data.username, data.email, data.password, None, None, data.avatar
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
):
    await user_services.update_user(user_id, username, about=about, avatar=avatar)
    return ResponseModel(
        status_code=200, message=f"Successfully updated user with id: {user_id}!"
    )


@user_router.delete("/{user_id}", response_model=ResponseModel)
async def delete_user_endpoint(user_id: int):
    await user_services.delete_user(user_id)
    return ResponseModel(
        status_code=200, message=f"Successfully deleted user with id: {user_id}!"
    )
