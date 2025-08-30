import logging
from typing import Annotated

from fastapi import APIRouter, UploadFile, File, Form, Body, Depends

from app.services.auth_services.auth0 import get_auth0_service, Auth0UserServices
from app.utils.token import token_services
from app.schemas.response_models import ResponseModel
from app.schemas.user import SignInRequestModel, SignUpRequestModel

auth_router = APIRouter(tags=["Auth0 Authentication"], prefix="/auth")

logger = logging.getLogger(__name__)


@auth_router.post("/", response_model=ResponseModel)
async def auth_user(
    avatar: UploadFile = File(None),
    name: str = Form(...),
    email: Annotated[str | None, Depends(token_services.get_data_from_token)] = None,
    auth0_service: Auth0UserServices = Depends(get_auth0_service),
):
    return await auth0_service.auth_user(
        name,
        avatar,
        email,
    )


@auth_router.post("/login")
async def login(
    data: SignInRequestModel = Body(),
    auth0_service: Auth0UserServices = Depends(get_auth0_service),
):
    return await auth0_service.login_user(data.email, data.password)


@auth_router.post("/register")
async def signup(
    data: SignUpRequestModel,
    auth0_service: Auth0UserServices = Depends(get_auth0_service),
):
    return await auth0_service.register_user(data.username, data.email, data.password)
