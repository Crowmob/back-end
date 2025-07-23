from fastapi import APIRouter

from app.schemas.response_models import HealthCheckModel

main_router = APIRouter(tags=["main"])


@main_router.get("/", response_model=HealthCheckModel)
def health_check():
    return HealthCheckModel(status_code=200, detail="ok", result="working")
