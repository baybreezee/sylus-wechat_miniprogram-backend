import os
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, Depends, UploadFile, File, Query
from app.config.database import album_collection
from app.models.user import UserInDB
from app.models.album import UploadPhoto
from app.utils.auth import get_current_active_user
from app.config.settings import UPLOAD_FOLDER
from bson import ObjectId

# 获取相册列表
async def get_photos(
    limit: int = Query(20, ge=1, le=100),
    before_date: Optional[datetime] = None,
    current_user: UserInDB = Depends(get_current_active_user)
):
    try:
        # 构建查询条件
        query = {}
        
        # 当前用户的照片
        user_id = str(current_user.id) if current_user.id else current_user.openid
        query["user_id"] = user_id
        
        if before_date:
            query["upload_date"] = {"$lt": before_date}
        
        # 获取照片，按上传日期倒序排列
        photos = list(album_collection.find(query).sort("upload_date", -1).limit(limit))
        
        # 转换为响应格式
        result = []
        for photo in photos:
            result.append({
                "id": str(photo["_id"]),
                "user_id": photo["user_id"],
                "uploader_name": photo["uploader_name"],
                "uploader_type": photo["uploader_type"],
                "image_url": photo["image_url"],
                "caption": photo.get("caption"),
                "location": photo.get("location"),
                "upload_date": photo["upload_date"]
            })
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取相册列表失败: {str(e)}")

# 上传照片
async def upload_photo(
    photo_info: UploadPhoto,
    file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_active_user)
):
    try:
        # 验证文件类型
        allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="不支持的文件类型，仅支持JPEG、PNG、GIF和WEBP格式")
        
        # 创建用户上传目录
        album_dir = os.path.join(UPLOAD_FOLDER, "albums", str(current_user.id) if current_user.id else current_user.openid)
        os.makedirs(album_dir, exist_ok=True)
        
        # 生成唯一文件名
        file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(album_dir, unique_filename)
        
        # 保存文件
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # 照片URL
        image_url = f"/static/uploads/albums/{str(current_user.id) if current_user.id else current_user.openid}/{unique_filename}"
        
        # 创建照片记录
        now = datetime.utcnow()
        new_photo = {
            "user_id": str(current_user.id) if current_user.id else current_user.openid,
            "uploader_name": current_user.nickname or "用户",
            "uploader_type": "user",
            "image_url": image_url,
            "caption": photo_info.caption,
            "location": photo_info.location,
            "upload_date": now
        }
        
        # 存储照片记录
        result = album_collection.insert_one(new_photo)
        photo_id = result.inserted_id
        
        # 返回已上传的照片信息
        return {
            "id": str(photo_id),
            "user_id": new_photo["user_id"],
            "uploader_name": new_photo["uploader_name"],
            "uploader_type": new_photo["uploader_type"],
            "image_url": new_photo["image_url"],
            "caption": new_photo["caption"],
            "location": new_photo["location"],
            "upload_date": new_photo["upload_date"]
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"上传照片失败: {str(e)}")