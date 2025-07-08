from fastapi import APIRouter
from app.schemas.response_models import UserResponse

main_router = APIRouter(tags=["main"])


@main_router.get("/", response_model=UserResponse)
def health_check():
    return {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }