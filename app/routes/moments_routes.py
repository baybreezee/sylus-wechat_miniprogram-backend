from fastapi import APIRouter, Depends, Query, File, UploadFile
from typing import Optional
from datetime import datetime
from app.controllers.moments_controller import (
    get_moments, create_moment, upload_moment_image,
    like_moment, comment_moment, get_ai_moment_response,
    delete_moment, delete_comment, upload_moments_background,
    get_moments_background
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
    """对指定朋友圈动态进行点赞/取消点赞操作"""
    return await like_moment(moment_id, current_user)

@router.post("/{moment_id}/comment")
async def comment(
    moment_id: str,
    comment: CreateComment,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """对指定朋友圈动态发表评论"""
    return await comment_moment(moment_id, comment, current_user)

@router.post("/{moment_id}/ai-response")
async def ai_response(
    moment_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """获取Sylus对用户朋友圈的AI回应"""
    request = MomentAIResponseRequest(moment_id=moment_id)
    return await get_ai_moment_response(request, current_user)

@router.delete("/{moment_id}")
async def delete(
    moment_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """删除指定的朋友圈动态"""
    return await delete_moment(moment_id, current_user)

@router.delete("/{moment_id}/comments/{comment_id}")
async def delete_comment_route(
    moment_id: str,
    comment_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """删除指定的朋友圈评论"""
    return await delete_comment(moment_id, comment_id, current_user)

@router.post("/background")
async def upload_background(
    file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """上传朋友圈背景图片"""
    return await upload_moments_background(file, current_user)

@router.get("/background/{openid}/{filename}")
async def get_background(openid: str, filename: str):
    """获取朋友圈背景图片"""
    return await get_moments_background(openid, filename) 