from fastapi import APIRouter, Depends
from app.controllers.relationship_controller import get_relationship_info, update_relationship
from app.models.user import UserInDB
from app.models.relationship import RelationshipUpdate
from app.utils.auth import get_current_active_user

router = APIRouter(prefix="/api/relationship", tags=["关系"])

@router.get("/info")
async def relationship_info(current_user: UserInDB = Depends(get_current_active_user)):
    """获取用户与Sylus的关系信息"""
    return await get_relationship_info(current_user)

@router.get("/status")
async def relationship_status(current_user: UserInDB = Depends(get_current_active_user)):
    """获取用户与Sylus的关系状态（别名）"""
    return await get_relationship_info(current_user)

@router.put("/update")
async def update_relationship_status(relationship_update: RelationshipUpdate, current_user: UserInDB = Depends(get_current_active_user)):
    """更新关系状态信息"""
    return await update_relationship(relationship_update, current_user) 