from fastapi import APIRouter, Depends, Body

from app.schemas.admin import AdminActionRequest
from app.schemas.membership import GetAllAdminsRequest
from app.schemas.response_models import ListResponse, ResponseModel
from app.schemas.user import MemberDetailResponse
from app.services.admin import admin_services

admin_router = APIRouter(tags=["Admin"], prefix="/admins")


@admin_router.get("/", response_model=ListResponse[MemberDetailResponse])
async def get_all_admins(data: GetAllAdminsRequest = Depends()):
    return await admin_services.get_all_admins(data.company_id, data.limit, data.offset)


@admin_router.put("/", response_model=ResponseModel)
async def appoint_admin(data: AdminActionRequest = Body(...)):
    await admin_services.appoint_admin(data.user_id, data.company_id)
    return ResponseModel(status_code=200, message="Appointed admin successfully")


@admin_router.delete("/", response_model=ResponseModel)
async def remove_admin(data: AdminActionRequest = Body(...)):
    await admin_services.remove_admin(data.user_id, data.company_id)
    return ResponseModel(status_code=200, message="Removed admin successfully")
