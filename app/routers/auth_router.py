from fastapi import APIRouter, Depends

from app.services.auth_services.auth0 import auth0_user_services
from app.services.token import token_services
from app.schemas.response_models import ResponseModel

auth_router = APIRouter(tags=["Auth0 Authentication"], prefix="/auth")


@auth_router.get("/{token}", response_model=ResponseModel)
async def auth_user(data: dict = Depends(token_services.get_data_from_token)):
    email = await auth0_user_services.auth_user(
        data["http://localhost:8000/email"], data["sub"]
    )
    return ResponseModel(
        status_code=200, message=f"Successfully authenticated user with email: {email}"
    )
