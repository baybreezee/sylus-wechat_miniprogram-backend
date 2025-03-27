from fastapi import HTTPException, Depends, Body
from app.config.database import sylus_collection
from app.models.user import UserInDB
from app.utils.auth import get_current_active_user
from bson import ObjectId
from datetime import datetime
from typing import Optional

# 获取Sylus信息
async def get_sylus_info(current_user: UserInDB = Depends(get_current_active_user)):
    # 从数据库获取Sylus信息
    sylus = sylus_collection.find_one()
    
    if not sylus:
        raise HTTPException(status_code=404, detail="Sylus信息未找到")
    
    # 返回Sylus信息
    return {
        "id": str(sylus["_id"]),
        "name": sylus["name"],
        "avatar": sylus["avatar"],
        "signature": sylus["signature"],
        "tags": sylus["tags"],
        "personality": sylus["personality"],
        "created_at": sylus["created_at"]
    }

# 更新Sylus昵称
async def update_sylus_name(
    name: str = Body(..., embed=True), 
    current_user: UserInDB = Depends(get_current_active_user)
):
    try:
        # 检查名称长度
        if len(name) < 1 or len(name) > 20:
            raise HTTPException(status_code=400, detail="昵称长度必须在1-20个字符之间")
        
        # 获取当前Sylus信息
        sylus = sylus_collection.find_one()
        if not sylus:
            raise HTTPException(status_code=404, detail="Sylus信息未找到")
        
        # 更新昵称
        result = sylus_collection.update_one(
            {"_id": sylus["_id"]},
            {"$set": {"name": name, "updated_at": datetime.utcnow()}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="更新Sylus昵称失败")
        
        # 返回更新后的信息
        updated_sylus = sylus_collection.find_one({"_id": sylus["_id"]})
        return {
            "id": str(updated_sylus["_id"]),
            "name": updated_sylus["name"],
            "avatar": updated_sylus["avatar"],
            "signature": updated_sylus["signature"],
            "tags": updated_sylus["tags"],
            "personality": updated_sylus["personality"],
            "created_at": updated_sylus["created_at"],
            "updated_at": updated_sylus.get("updated_at")
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"更新Sylus昵称时出错: {str(e)}") 