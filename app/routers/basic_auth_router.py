from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.response_models import MeResponseModel, AuthResponseModel
from app.schemas.user import SignUpRequestModel, SignInRequestModel
from app.services.user import UserServices
from app.utils.token import create_access_token, decode_token
from app.utils.password import check_password

basic_auth_router = APIRouter(tags=["Basic Authentication"], prefix="user")
user_services = UserServices()


@basic_auth_router.post("/register", response_model=AuthResponseModel)
async def register(data: SignUpRequestModel = Depends()):
    user_id = await user_services.create_user(
        data.username, data.email, data.password, None, None
    )
    token = create_access_token(user_id)
    return AuthResponseModel(
        status_code=200, message="Registered successfully!", token=token
    )


@basic_auth_router.post("/login", response_model=AuthResponseModel)
async def login(data: SignInRequestModel = Depends()):
    user = await user_services.get_user_by_email(data.email)
    if check_password(data.password, user.password):
        token = create_access_token(user.id)
        return AuthResponseModel(status_code=200, message="Logged in", token=token)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong password."
        )


@basic_auth_router.get("/me", response_model=MeResponseModel)
async def get_me(token: str):
    data = decode_token(token)
    user = await user_services.get_user_by_id(data["id"])
    return MeResponseModel(status_code=200, me=user)
