from fastapi import APIRouter, Body, Header
import logging

from app.services.auth_services.auth0 import auth0_user_services
from app.utils.token import token_services
from app.schemas.response_models import ResponseModel
from app.schemas.user import SignInRequestModel, SignUpRequestModel, Username

auth_router = APIRouter(tags=["Auth0 Authentication"], prefix="/auth")

logger = logging.getLogger(__name__)


@auth_router.post("/", response_model=ResponseModel)
async def auth_user(body: Username = Body(...), authorization: str = Header(...)):
    token = authorization.removeprefix("Bearer ")
    data = await token_services.get_data_from_token(token)
    email = await auth0_user_services.auth_user(
        body.name, body.avatar, data["http://localhost:8000/email"], data["sub"]
    )
    return ResponseModel(
        status_code=200,
        message=f"Successfully authenticated user with email: {email}",
    )


@auth_router.post("/login")
async def login(data: SignInRequestModel):
    return await auth0_user_services.login_user(data.email, data.password)


@auth_router.post("/register")
async def signup(data: SignUpRequestModel):
    return await auth0_user_services.register_user(
        data.username, data.email, data.password
    )
