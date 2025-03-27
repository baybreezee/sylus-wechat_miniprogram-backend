from fastapi import APIRouter, Depends, File, UploadFile
from app.controllers.user_controller import (
    get_user_info, update_user_info, upload_avatar, 
    upload_profile_background, get_profile_background
)
from app.controllers.auth_controller import wechat_login
from app.models.user import UserUpdate, UserInDB, UserLogin
from app.utils.auth import get_current_active_user
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
import os
from app.config.settings import UPLOAD_FOLDER
import logging
import mimetypes
import io

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

@router.post("/background")
async def upload_user_background(file: UploadFile = File(...), current_user: UserInDB = Depends(get_current_active_user)):
    """上传并更新用户个人资料背景图片"""
    return await upload_profile_background(file, current_user)

@router.get("/avatar/{openid}/{filename}")
async def get_user_avatar(openid: str, filename: str):
    """获取用户头像图片"""
    logger = logging.getLogger("uvicorn")
    
    try:
        # 构建文件路径
        file_path = os.path.join(UPLOAD_FOLDER, "avatars", openid, filename)
        logger.info(f"请求头像文件路径: {file_path}")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            logger.error(f"头像文件不存在: {file_path}")
            return JSONResponse(
                status_code=404,
                content={"detail": "头像不存在"}
            )
        
        # 确定内容类型
        content_type, _ = mimetypes.guess_type(file_path)
        if not content_type:
            if filename.lower().endswith(".jpg") or filename.lower().endswith(".jpeg"):
                content_type = "image/jpeg"
            elif filename.lower().endswith(".png"):
                content_type = "image/png"
            elif filename.lower().endswith(".gif"):
                content_type = "image/gif"
            elif filename.lower().endswith(".webp"):
                content_type = "image/webp"
            else:
                content_type = "application/octet-stream"
        
        logger.info(f"文件MIME类型: {content_type}")
        
        # 读取文件内容
        try:
            file_content = open(file_path, "rb").read()
            logger.info(f"文件大小: {len(file_content)} 字节")
            
            # 使用StreamingResponse返回文件
            return StreamingResponse(
                io.BytesIO(file_content),
                media_type=content_type,
                headers={
                    "Content-Disposition": f"inline; filename={filename}",
                    "Access-Control-Allow-Origin": "*"
                }
            )
            
        except Exception as e:
            logger.error(f"文件访问错误: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"detail": f"文件访问出错: {str(e)}"}
            )
    except Exception as e:
        logger.error(f"获取头像异常: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"服务器错误: {str(e)}"}
        )

@router.get("/background/{openid}/{filename}")
async def get_user_background(openid: str, filename: str):
    """获取用户个人资料背景图片"""
    return await get_profile_background(openid, filename) 