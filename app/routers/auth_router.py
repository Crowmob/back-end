from fastapi import APIRouter, Depends

from app.auth import get_data_from_token

auth_router = APIRouter(tags=["Auth0 Authentication"])


@auth_router.get("/private")
def private(data: dict = Depends(get_data_from_token)):
    return {"message": f"user: {data}"}
