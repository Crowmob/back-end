import os
import shutil
import glob

from fastapi import APIRouter, Depends, Header, Response, Form, UploadFile, File

from app.services.user import user_services
from app.utils.token import token_services
from app.schemas.user import (
    GetAllUsersRequestModel,
    SignUpRequestModel,
    UserUpdateRequestModel,
    UserDetailResponse,
    ListResponse,
)
from app.schemas.response_models import ResponseModel

user_router = APIRouter(tags=["User CRUD"], prefix="/users")


@user_router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user_by_id_endpoint(user_id: int, authorization: str = Header(...)):
    token = authorization.removeprefix("Bearer ")
    data = await token_services.get_data_from_token(token)
    user_data = await user_services.get_user_by_id(user_id)
    if data["http://localhost:8000/email"] == user_data.email:
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
    ext = avatar.filename.split(".")[-1]
    filename = f"{user_id}.{ext}"
    filepath = os.path.join("static/avatars/", filename)
    pattern = f"/static/avatars/{user_id}.*"
    matches = glob.glob(pattern)
    if matches:
        for file_path in matches:
            os.remove(file_path)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(avatar.file, buffer)
    await user_services.update_user(user_id, username, about=about, avatar_ext=ext)
    return ResponseModel(
        status_code=200, message=f"Successfully updated user with id: {user_id}!"
    )


@user_router.delete("/{user_id}", response_model=ResponseModel)
async def delete_user_endpoint(user_id: int):
    await user_services.delete_user(user_id)
    return ResponseModel(
        status_code=200, message=f"Successfully deleted user with id: {user_id}!"
    )
