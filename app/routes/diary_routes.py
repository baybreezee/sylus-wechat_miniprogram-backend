from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from datetime import date
from app.controllers.diary_controller import create_diary, get_diary_by_id, get_diaries, update_diary, delete_diary, get_ai_diary_response
from app.models.user import UserInDB
from app.models.diary import DiaryCreate, DiaryUpdate, DiaryAIResponseRequest
from app.utils.auth import get_current_active_user

router = APIRouter(prefix="/api/diary", tags=["日记"])

@router.get("/list")
async def list_diaries(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """获取用户的日记列表"""
    return await get_diaries(start_date, end_date, page, page_size, current_user)

@router.post("")
async def add_diary(diary: DiaryCreate, current_user: UserInDB = Depends(get_current_active_user)):
    """创建新的日记"""
    return await create_diary(diary, current_user)

@router.post("/ai-response")
async def get_ai_response(request: DiaryAIResponseRequest, current_user: UserInDB = Depends(get_current_active_user)):
    """获取AI对日记的回复"""
    return await get_ai_diary_response(request, current_user)

@router.get("/{diary_id}")
async def get_diary(diary_id: str, current_user: UserInDB = Depends(get_current_active_user)):
    """根据ID获取日记详情"""
    return await get_diary_by_id(diary_id, current_user)

@router.put("/{diary_id}")
async def edit_diary(
    diary_id: str,
    diary_update: DiaryUpdate,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """更新日记内容"""
    return await update_diary(diary_id, diary_update, current_user)

@router.delete("/{diary_id}")
async def remove_diary(diary_id: str, current_user: UserInDB = Depends(get_current_active_user)):
    """删除日记"""
    return await delete_diary(diary_id, current_user) 