from fastapi import APIRouter, Depends, Header
from typing import Annotated

from app.schemas.response_models import MeResponseModel, AuthResponseModel
from app.schemas.user import SignUpRequestModel, SignInRequestModel
from app.services.auth_services.basic import get_basic_auth_service, BasicAuthServices
from app.utils.token import token_services

basic_auth_router = APIRouter(tags=["Basic Authentication"], prefix="/user")


@basic_auth_router.post("/register", response_model=AuthResponseModel)
async def register(
    data: SignUpRequestModel = Depends(),
    basic_auth_service: BasicAuthServices = Depends(get_basic_auth_service),
):
    return await basic_auth_service.register(data.username, data.email, data.password)


@basic_auth_router.post("/login", response_model=AuthResponseModel)
async def login(
    data: SignInRequestModel = Depends(),
    basic_auth_service: BasicAuthServices = Depends(get_basic_auth_service),
):
    return await basic_auth_service.login(data.email, data.password)


@basic_auth_router.get("/me", response_model=MeResponseModel)
async def get_me(
    email: Annotated[str | None, Depends(token_services.get_data_from_token)],
    basic_auth_service: BasicAuthServices = Depends(get_basic_auth_service),
):
    return await basic_auth_service.get_me(email)
