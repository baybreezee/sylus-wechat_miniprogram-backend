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