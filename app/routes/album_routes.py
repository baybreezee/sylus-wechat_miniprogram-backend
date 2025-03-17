from fastapi import APIRouter, Depends, Query, File, UploadFile
from typing import Optional
from datetime import datetime
from app.controllers.album_controller import get_photos, upload_photo
from app.models.user import UserInDB
from app.models.album import UploadPhoto
from app.utils.auth import get_current_active_user

router = APIRouter(prefix="/api/album", tags=["相册"])

@router.get("/list")
async def album_list(
    limit: int = Query(20, ge=1, le=100),
    before_date: Optional[datetime] = None,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """获取共同相册的照片列表"""
    return await get_photos(limit, before_date, current_user)

@router.post("/upload-photo")
async def upload_new_photo(
    photo_info: UploadPhoto,
    file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """上传新照片到共同相册"""
    return await upload_photo(photo_info, file, current_user) 