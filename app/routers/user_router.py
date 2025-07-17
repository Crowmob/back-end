from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.services.user import UserServices
from app.schemas.user import (
    GetAllUsersRequestModel,
    SignUpRequestModel,
    UserUpdateRequestModel,
)
from app.core.exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    UserUpdateException,
)
from app.schemas.user import UserDetailResponse, ListResponse

user_router = APIRouter(tags=["User CRUD"])
user_services = UserServices()


@user_router.get("/get_user_by_id", response_model=UserDetailResponse)
async def get_user_by_id(user_id: int):
    try:
        return await user_services.get_user_by_id(user_id)
    except UserNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@user_router.get("/get_all_users", response_model=ListResponse[UserDetailResponse])
async def get_all_users(data: GetAllUsersRequestModel = Depends()):
    return await user_services.get_all_users(data)


@user_router.post("/create_user")
async def create_user(user_data: SignUpRequestModel):
    try:
        user_id = await user_services.create_user(user_data)
    except UserAlreadyExistsException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    return JSONResponse(
        status_code=200,
        content={"message": f"Created user successfully! id: {user_id}"},
    )


@user_router.put("/update_user")
async def update_user(user_id: int, update_data: UserUpdateRequestModel = Depends()):
    try:
        await user_services.update_user(user_id, update_data)
    except UserNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except UserUpdateException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    return JSONResponse(
        status_code=200,
        content={"message": f"Successfully updated user with id: {user_id}!"},
    )


@user_router.delete("/delete_user")
async def delete_user(user_id: int):
    try:
        await user_services.delete_user(user_id)
    except UserNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    return JSONResponse(
        status_code=200,
        content={"message": f"Successfully deleted user with id: {user_id}!"},
    )
