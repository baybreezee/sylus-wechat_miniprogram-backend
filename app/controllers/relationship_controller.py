from datetime import datetime, timezone
from fastapi import HTTPException, Depends
from app.config.database import relationship_collection, sylus_collection
from app.models.user import UserInDB
from app.models.relationship import RelationshipUpdate
from app.utils.auth import get_current_active_user
from bson import ObjectId

# 获取关系信息
async def get_relationship_info(current_user: UserInDB = Depends(get_current_active_user)):
    # 获取Sylus ID
    sylus = sylus_collection.find_one()
    if not sylus:
        raise HTTPException(status_code=404, detail="Sylus信息未找到")
    
    sylus_id = str(sylus["_id"])
    
    # 查找关系信息
    relationship = relationship_collection.find_one({
        "user_id": str(current_user.id) if current_user.id else current_user.openid,
        "sylus_id": sylus_id
    })
    
    # 如果关系不存在，则创建一个新的
    if not relationship:
        now = datetime.now(timezone.utc)
        new_relationship = {
            "user_id": str(current_user.id) if current_user.id else current_user.openid,
            "sylus_id": sylus_id,
            "start_date": now,
            "sweetness": 0,
            "level": 1,
            "chat_days": 0,  # 初始化聊天天数为0
            "milestones": [],
            "created_at": now,
            "updated_at": now
        }
        
        result = relationship_collection.insert_one(new_relationship)
        relationship = relationship_collection.find_one({"_id": result.inserted_id})
    
    # 计算在一起的天数
    start_date = relationship["start_date"]
    # 确保start_date是带时区的datetime
    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=timezone.utc)
    
    days_together = (datetime.now(timezone.utc) - start_date).days
    
    return {
        "id": str(relationship["_id"]),
        "user_id": relationship["user_id"],
        "sylus_id": relationship["sylus_id"],
        "start_date": relationship["start_date"],
        "days_together": days_together,
        "sweetness": relationship["sweetness"],
        "level": relationship["level"],
        "chat_days": relationship.get("chat_days", 0),  # 获取聊天天数，默认为0
        "milestones": relationship["milestones"],
        "created_at": relationship["created_at"],
        "updated_at": relationship["updated_at"]
    }

# 更新关系状态
async def update_relationship(
    relationship_update: RelationshipUpdate,
    current_user: UserInDB = Depends(get_current_active_user)
):
    # 获取Sylus ID
    sylus = sylus_collection.find_one()
    if not sylus:
        raise HTTPException(status_code=404, detail="Sylus信息未找到")
    
    sylus_id = str(sylus["_id"])
    
    # 查找关系信息
    relationship = relationship_collection.find_one({
        "user_id": str(current_user.id) if current_user.id else current_user.openid,
        "sylus_id": sylus_id
    })
    
    if not relationship:
        raise HTTPException(status_code=404, detail="关系信息未找到")
    
    # 准备更新数据
    update_data = {
        "updated_at": datetime.now(timezone.utc)
    }
    
    # 更新甜蜜值
    if relationship_update.sweetness_delta is not None:
        new_sweetness = relationship["sweetness"] + relationship_update.sweetness_delta
        update_data["sweetness"] = max(0, new_sweetness)  # 确保不为负数
        
        # 更新等级（根据甜蜜值）
        if new_sweetness >= 1000:
            update_data["level"] = 10
        elif new_sweetness >= 800:
            update_data["level"] = 8
        elif new_sweetness >= 600:
            update_data["level"] = 6
        elif new_sweetness >= 400:
            update_data["level"] = 4
        elif new_sweetness >= 200:
            update_data["level"] = 2
        else:
            update_data["level"] = 1
    
    # 更新数据库
    result = relationship_collection.update_one(
        {"_id": relationship["_id"]},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="关系更新失败")
    
    # 获取更新后的关系信息
    updated_relationship = relationship_collection.find_one({"_id": relationship["_id"]})
    
    # 计算在一起的天数
    start_date = updated_relationship["start_date"]
    # 确保start_date是带时区的datetime
    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=timezone.utc)
    
    days_together = (datetime.now(timezone.utc) - start_date).days
    
    return {
        "id": str(updated_relationship["_id"]),
        "user_id": updated_relationship["user_id"],
        "sylus_id": updated_relationship["sylus_id"],
        "start_date": updated_relationship["start_date"],
        "days_together": days_together,
        "sweetness": updated_relationship["sweetness"],
        "level": updated_relationship["level"],
        "chat_days": updated_relationship.get("chat_days", 0),  # 获取聊天天数，默认为0
        "milestones": updated_relationship["milestones"],
        "created_at": updated_relationship["created_at"],
        "updated_at": updated_relationship["updated_at"]
    } 