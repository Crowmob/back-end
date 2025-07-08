from fastapi import APIRouter
from app.schemas.response_models import UserResponseSchema

main_router = APIRouter(tags=["main"])


@main_router.get("/")
def health_check():
    return UserResponseSchema(
        status_code=200,
        detail="ok",
        result="working"
    )