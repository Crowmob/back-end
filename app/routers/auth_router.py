from fastapi import APIRouter, Depends

from app.auth import get_data_from_token
from app.services.user import UserServices

auth_router = APIRouter(tags=["Auth0 Authentication"], prefix="/auth")
user_services = UserServices()


@auth_router.get("/{token}")
async def auth_user(data: dict = Depends(get_data_from_token)):
    email = data["http://localhost:8000/email"]
    sub = data["sub"].split("|")
    auth_provider = sub[0]
    oauth_id = sub[1]
    await user_services.create_user(None, email, None, auth_provider, oauth_id)
    return {"email": email, "provider": auth_provider, "id": oauth_id}
