from fastapi import HTTPException, Depends
from app.config.database import sylus_collection
from app.models.user import UserInDB
from app.utils.auth import get_current_active_user
from bson import ObjectId

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