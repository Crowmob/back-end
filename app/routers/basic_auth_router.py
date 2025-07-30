from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.response_models import MeResponseModel, AuthResponseModel
from app.schemas.user import SignUpRequestModel, SignInRequestModel
from app.services.auth_services.basic import basic_auth_services
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
async def get_me(token: str):
    user = await basic_auth_services.get_me(token)
    return MeResponseModel(status_code=200, me=user)
