from fastapi import APIRouter, Depends, File, UploadFile
from app.controllers.user_controller import get_user_info, update_user_info, upload_avatar
from app.controllers.auth_controller import wechat_login
from app.models.user import UserUpdate, UserInDB, UserLogin
from app.utils.auth import get_current_active_user

router = APIRouter(prefix="/api/users", tags=["用户"])

@router.post("/login")
async def login(login_data: UserLogin):
    """用户登录认证"""
    return await wechat_login(login_data)

@router.get("/me")
async def user_info(current_user: UserInDB = Depends(get_current_active_user)):
    """获取当前登录用户的基本信息"""
    return await get_user_info(current_user)

@router.put("/me")
async def update_user(user_update: UserUpdate, current_user: UserInDB = Depends(get_current_active_user)):
    """更新用户的基本信息"""
    return await update_user_info(user_update, current_user)

@router.post("/avatar")
async def upload_user_avatar(file: UploadFile = File(...), current_user: UserInDB = Depends(get_current_active_user)):
    """上传并更新用户头像"""
    return await upload_avatar(file, current_user) 