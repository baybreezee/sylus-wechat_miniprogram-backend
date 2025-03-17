from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.controllers.auth_controller import wechat_login, login_for_access_token
from app.models.user import UserLogin

# 认证路由
router = APIRouter(prefix="/api/auth", tags=["认证"])

# 登录接口添加到users路由下，保持与测试脚本一致
@router.post("/login")
async def login(login_data: UserLogin):
    """用户登录认证"""
    return await wechat_login(login_data)

@router.post("/token")
async def get_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """获取访问API的认证令牌（用于测试）"""
    return await login_for_access_token(form_data) 