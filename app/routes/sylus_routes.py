from fastapi import APIRouter, Depends, Body
from app.controllers.sylus_controller import get_sylus_info, update_sylus_name
from app.models.user import UserInDB
from app.utils.auth import get_current_active_user

router = APIRouter(prefix="/api/sylus", tags=["Sylus"])

@router.get("/info")
async def sylus_info(current_user: UserInDB = Depends(get_current_active_user)):
    """获取AI伴侣Sylus的基本信息"""
    return await get_sylus_info(current_user)

@router.put("/update-name")
async def update_name(
    name: str = Body(..., embed=True),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """更新Sylus的昵称"""
    return await update_sylus_name(name, current_user) 