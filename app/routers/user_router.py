from fastapi import APIRouter, Depends

from app.services.user import UserServices
from app.schemas.user import (
    GetAllUsersRequestModel,
    SignUpRequestModel,
    UserUpdateRequestModel,
    UserDetailResponse,
    ListResponse,
)
from app.schemas.response_models import ResponseModel

user_router = APIRouter(tags=["User CRUD"])
user_services = UserServices()


@user_router.get("/get_user_by_id", response_model=UserDetailResponse)
async def get_user_by_id_endpoint(user_id: int):
    return await user_services.get_user_by_id(user_id)


@user_router.get("/get_user_by_email", response_model=UserDetailResponse)
async def get_user_by_email_endpoint(email: str):
    return await user_services.get_user_by_email(email)


@user_router.get("/get_all_users", response_model=ListResponse[UserDetailResponse])
async def get_all_users_endpoint(data: GetAllUsersRequestModel = Depends()):
    return await user_services.get_all_users(data.limit, data.offset)


@user_router.post("/create_user", response_model=ResponseModel)
async def create_user_endpoint(user_data: SignUpRequestModel):
    user_id = await user_services.create_user(
        user_data.username, user_data.email, user_data.password, None, None
    )
    return ResponseModel(
        status_code=200, message=f"Created user successfully! id: {user_id}"
    )


@user_router.put("/update_user", response_model=ResponseModel)
async def update_user_endpoint(
    user_id: int, update_data: UserUpdateRequestModel = Depends()
):
    await user_services.update_user(
        user_id, update_data.username, update_data.email, update_data.password
    )
    return ResponseModel(
        status_code=200, message=f"Successfully updated user with id: {user_id}!"
    )


@user_router.delete("/delete_user", response_model=ResponseModel)
async def delete_user_endpoint(user_id: int):
    await user_services.delete_user(user_id)
    return ResponseModel(
        status_code=200, message=f"Successfully deleted user with id: {user_id}!"
    )
