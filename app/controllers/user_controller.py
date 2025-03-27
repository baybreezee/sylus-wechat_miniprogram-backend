import os
import uuid
from datetime import datetime
from fastapi import HTTPException, Depends, UploadFile, File
from app.config.database import users_collection
from app.models.user import User, UserUpdate, UserInDB, UserAvatarResponse
from app.utils.auth import get_current_active_user
from app.config.settings import UPLOAD_FOLDER

# 获取用户信息
async def get_user_info(current_user: UserInDB = Depends(get_current_active_user)):
    # 直接返回当前用户信息
    return {
        "id": str(current_user.id) if current_user.id else None,
        "openid": current_user.openid,
        "nickname": current_user.nickname,
        "avatar": current_user.avatar,
        "signature": current_user.signature,
        "tags": current_user.tags
    }

# 更新用户信息
async def update_user_info(user_update: UserUpdate, current_user: UserInDB = Depends(get_current_active_user)):
    # 准备更新数据
    update_data = {
        "updated_at": datetime.utcnow()
    }
    
    # 只更新提供的字段
    if user_update.nickname is not None:
        update_data["nickname"] = user_update.nickname
    if user_update.signature is not None:
        update_data["signature"] = user_update.signature
    if user_update.tags is not None:
        update_data["tags"] = user_update.tags
    
    # 更新用户信息
    result = users_collection.update_one(
        {"openid": current_user.openid},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="用户信息更新失败")
    
    # 获取更新后的用户信息
    updated_user = users_collection.find_one({"openid": current_user.openid})
    
    return {
        "id": str(updated_user["_id"]) if "_id" in updated_user else None,
        "openid": updated_user["openid"],
        "nickname": updated_user.get("nickname"),
        "avatar": updated_user.get("avatar"),
        "signature": updated_user.get("signature"),
        "tags": updated_user.get("tags", [])
    }

# 上传用户头像
async def upload_avatar(file: UploadFile = File(...), current_user: UserInDB = Depends(get_current_active_user)):
    # 验证文件类型
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="不支持的文件类型，仅支持JPEG、PNG、GIF和WEBP格式")
    
    # 创建用户上传目录
    avatar_dir = os.path.join(UPLOAD_FOLDER, "avatars", current_user.openid)
    os.makedirs(avatar_dir, exist_ok=True)
    
    # 生成唯一文件名
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(avatar_dir, unique_filename)
    
    # 保存文件
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # 更新数据库中的头像URL - 使用新的API端点格式
    avatar_url = f"/api/users/avatar/{current_user.openid}/{unique_filename}"
    
    # 更新用户头像
    result = users_collection.update_one(
        {"openid": current_user.openid},
        {"$set": {"avatar": avatar_url, "updated_at": datetime.utcnow()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="头像更新失败")
    
    return UserAvatarResponse(avatar_url=avatar_url)

# 上传个人资料背景图片
async def upload_profile_background(file: UploadFile = File(...), current_user: UserInDB = Depends(get_current_active_user)):
    # 验证文件类型
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="不支持的文件类型，仅支持JPEG、PNG、GIF和WEBP格式")
    
    # 创建用户上传目录
    background_dir = os.path.join(UPLOAD_FOLDER, "backgrounds", "profile", current_user.openid)
    os.makedirs(background_dir, exist_ok=True)
    
    # 生成唯一文件名
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(background_dir, unique_filename)
    
    # 保存文件
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # 更新数据库中的背景URL
    background_url = f"/api/users/background/{current_user.openid}/{unique_filename}"
    
    # 更新用户背景
    result = users_collection.update_one(
        {"openid": current_user.openid},
        {"$set": {"profile_background": background_url, "updated_at": datetime.utcnow()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="背景更新失败")
    
    return {"background_url": background_url}

# 获取个人资料背景图片
async def get_profile_background(openid: str, filename: str):
    import logging
    import mimetypes
    import io
    from fastapi.responses import StreamingResponse
    
    logger = logging.getLogger("uvicorn")
    
    try:
        # 构建文件路径
        file_path = os.path.join(UPLOAD_FOLDER, "backgrounds", "profile", openid, filename)
        logger.info(f"请求个人资料背景图片路径: {file_path}")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            logger.error(f"个人资料背景图片不存在: {file_path}")
            raise HTTPException(status_code=404, detail="背景图片不存在")
        
        # 确定内容类型
        content_type, _ = mimetypes.guess_type(file_path)
        if not content_type:
            if filename.lower().endswith((".jpg", ".jpeg")):
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
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"获取个人资料背景图片异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取背景图片失败: {str(e)}") 