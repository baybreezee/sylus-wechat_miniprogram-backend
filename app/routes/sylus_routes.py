from fastapi import APIRouter, Depends
from app.controllers.sylus_controller import get_sylus_info
from app.models.user import UserInDB
from app.utils.auth import get_current_active_user

router = APIRouter(prefix="/api/sylus", tags=["Sylus"])

@router.get("/info")
async def sylus_info(current_user: UserInDB = Depends(get_current_active_user)):
    """获取AI伴侣Sylus的基本信息"""
    return await get_sylus_info(current_user) 