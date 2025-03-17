from fastapi import APIRouter, Depends, Query, File, UploadFile
from typing import Optional
from datetime import datetime
from app.controllers.moments_controller import (
    get_moments, create_moment, upload_moment_image,
    like_moment, unlike_moment, comment_moment, get_ai_moment_response
)
from app.models.user import UserInDB
from app.models.moments import CreateMoment, CreateComment, MomentAIResponseRequest
from app.utils.auth import get_current_active_user

router = APIRouter(prefix="/api/moments", tags=["朋友圈"])

@router.get("")
async def moments_list(
    limit: int = Query(10, ge=1, le=100),
    before_timestamp: Optional[datetime] = None,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """获取朋友圈动态列表"""
    return await get_moments(limit, before_timestamp, current_user)

@router.post("")
async def create_new_moment(
    moment: CreateMoment,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """发布新的朋友圈动态"""
    return await create_moment(moment, current_user)

@router.post("/images")
async def upload_image(
    file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """上传朋友圈图片"""
    return await upload_moment_image(file, current_user)

@router.post("/{moment_id}/like")
async def like(
    moment_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """对指定朋友圈动态点赞"""
    return await like_moment(moment_id, current_user)

@router.delete("/{moment_id}/like")
async def unlike(
    moment_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """取消对指定朋友圈动态的点赞"""
    return await unlike_moment(moment_id, current_user)

@router.post("/{moment_id}/comment")
async def comment(
    moment_id: str,
    comment: CreateComment,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """对指定朋友圈动态发表评论"""
    return await comment_moment(moment_id, comment, current_user)

@router.post("/ai-response")
async def ai_response(
    request: MomentAIResponseRequest,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """获取Sylus对用户朋友圈的AI回应"""
    return await get_ai_moment_response(request, current_user) 