from fastapi import APIRouter, Depends, Header
from typing import Annotated

from app.schemas.response_models import MeResponseModel, AuthResponseModel
from app.schemas.user import SignUpRequestModel, SignInRequestModel
from app.services.auth_services.basic import basic_auth_services
from app.utils.token import token_services
from app.core.exceptions.auth_exceptions import UnauthorizedException

basic_auth_router = APIRouter(tags=["Basic Authentication"], prefix="/user")


@basic_auth_router.post("/register", response_model=AuthResponseModel)
async def register(data: SignUpRequestModel = Depends()):
    token = await basic_auth_services.register(data.username, data.email, data.password)
    return AuthResponseModel(
        status_code=200, message="Registered successfully!", token=token
    )


@basic_auth_router.post("/login", response_model=AuthResponseModel)
async def login(data: SignInRequestModel = Depends()):
    token = await basic_auth_services.login(data.email, data.password)
    if token:
        return AuthResponseModel(status_code=200, message="Logged in", token=token)
    else:
        raise UnauthorizedException(detail="Wrong password.")


@basic_auth_router.get("/me", response_model=MeResponseModel)
async def get_me(
    email: Annotated[str | None, Depends(token_services.get_data_from_token)],
):
    if not email:
        raise UnauthorizedException(detail="Invalid token.")
    user = await basic_auth_services.get_me(email)
    return MeResponseModel(status_code=200, me=user)
