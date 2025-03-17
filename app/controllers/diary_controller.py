import os
import uuid
from datetime import datetime, date
from typing import List, Optional
from fastapi import HTTPException, Depends, UploadFile, File, Query
from app.config.database import diary_collection, sylus_collection, get_database
from app.models.user import UserInDB
from app.models.diary import CreateDiary, DiaryAIResponseRequest, DiaryCreate, DiaryUpdate
from app.utils.auth import get_current_active_user
from app.services.ai_service import get_diary_response
from app.config.settings import UPLOAD_FOLDER
from bson import ObjectId
import bson.errors

# 获取日记列表
async def get_diaries(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = 1,
    page_size: int = 10,
    current_user: UserInDB = None
):
    """获取用户的日记列表"""
    db = get_database()
    
    try:
        # 构建查询条件
        query = {"user_id": str(current_user.id)}
        
        if start_date:
            query["date"] = {"$gte": start_date}
        
        if end_date:
            if "date" in query:
                query["date"]["$lte"] = end_date
            else:
                query["date"] = {"$lte": end_date}
        
        # 计算总数
        total = await db.diaries.count_documents(query)
        
        # 分页查询
        skip = (page - 1) * page_size
        diaries = await db.diaries.find(query).sort("date", -1).skip(skip).limit(page_size).to_list(page_size)
        
        # 转换ObjectId为字符串
        for diary in diaries:
            diary["id"] = str(diary["_id"])
            del diary["_id"]
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "diaries": diaries
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取日记列表出错: {str(e)}")

# 发布日记
async def create_diary(diary: DiaryCreate, current_user: UserInDB):
    """创建新的日记"""
    db = get_database()
    
    try:
        # 创建新日记
        current_datetime = datetime.now()
        
        # 如果提供了日期，将其转换为字符串，否则使用当前日期
        diary_date = diary.date.isoformat() if diary.date else current_datetime.date().isoformat()
        
        new_diary = {
            "user_id": str(current_user.id),
            "title": diary.title,
            "content": diary.content,
            "mood": diary.mood,
            "timestamp": current_datetime,
            "date": diary_date  # 存储为ISO格式的字符串
        }
        
        # 保存日记到数据库
        result = await db.diaries.insert_one(new_diary)
        
        # 返回保存的日记
        saved_diary = await db.diaries.find_one({"_id": result.inserted_id})
        saved_diary["id"] = str(saved_diary["_id"])
        del saved_diary["_id"]
        
        return saved_diary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建日记出错: {str(e)}")

# 获取AI日记回应
async def get_ai_diary_response(
    request: DiaryAIResponseRequest,
    current_user: UserInDB = Depends(get_current_active_user)
):
    try:
        # 查找日记
        diary = diary_collection.find_one({"_id": ObjectId(request.diary_id)})
        
        if not diary:
            raise HTTPException(status_code=404, detail="日记不存在")
        
        # 验证是否为当前用户的日记
        user_id = str(current_user.id) if current_user.id else current_user.openid
        if diary["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="无法访问其他用户的日记")
        
        # 获取Sylus信息
        sylus = sylus_collection.find_one()
        if not sylus:
            raise HTTPException(status_code=404, detail="Sylus信息未找到")
        
        # 从AI服务获取回复
        sylus_personality = sylus.get("personality", "温柔体贴，善解人意")
        ai_response = await get_diary_response(diary["content"], diary.get("mood"), sylus_personality)
        
        # 创建Sylus日记回应
        now = datetime.utcnow()
        today = date.today().isoformat()  # 存储为ISO格式的字符串
        
        # 设置默认心情为中性，如果AIResponse对象有mood属性则使用它
        mood = "neutral"
        if hasattr(ai_response, "mood"):
            mood = ai_response.mood
            
        sylus_diary = {
            "user_id": user_id,
            "author_name": sylus["name"],
            "author_type": "sylus",
            "content": ai_response.response,
            "mood": mood,
            "images": [],
            "date": today,
            "timestamp": now,
            "in_response_to": str(diary["_id"])
        }
        
        # 存储Sylus日记回应
        result = diary_collection.insert_one(sylus_diary)
        
        # 返回Sylus日记回应
        return {
            "id": str(result.inserted_id),
            "user_id": sylus_diary["user_id"],
            "author_name": sylus_diary["author_name"],
            "author_type": sylus_diary["author_type"],
            "content": sylus_diary["content"],
            "mood": sylus_diary["mood"],
            "images": sylus_diary["images"],
            "date": sylus_diary["date"],
            "timestamp": sylus_diary["timestamp"],
            "in_response_to": sylus_diary["in_response_to"]
        }
    except bson.errors.InvalidId:
        raise HTTPException(status_code=400, detail="无效的日记ID格式")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取AI日记回复出错: {str(e)}")

async def get_diary_by_id(diary_id: str, current_user: UserInDB):
    """根据ID获取日记详情"""
    db = get_database()
    
    try:
        # 查询日记
        diary = await db.diaries.find_one({"_id": ObjectId(diary_id), "user_id": str(current_user.id)})
        
        if not diary:
            raise HTTPException(status_code=404, detail="日记不存在或无权访问")
        
        # 转换ObjectId为字符串
        diary["id"] = str(diary["_id"])
        del diary["_id"]
        
        return diary
    except bson.errors.InvalidId:
        raise HTTPException(status_code=400, detail="无效的日记ID格式")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取日记详情出错: {str(e)}")

async def update_diary(diary_id: str, diary_update: DiaryUpdate, current_user: UserInDB):
    """更新日记内容"""
    db = get_database()
    
    # 查询日记是否存在
    diary = await db.diaries.find_one({"_id": ObjectId(diary_id), "user_id": str(current_user.id)})
    
    if not diary:
        raise HTTPException(status_code=404, detail="日记不存在或无权访问")
    
    # 构建更新数据
    update_data = {}
    if diary_update.title is not None:
        update_data["title"] = diary_update.title
    if diary_update.content is not None:
        update_data["content"] = diary_update.content
    if diary_update.mood is not None:
        update_data["mood"] = diary_update.mood
    if diary_update.date is not None:
        update_data["date"] = diary_update.date
    
    # 更新日记
    if update_data:
        await db.diaries.update_one(
            {"_id": ObjectId(diary_id)},
            {"$set": update_data}
        )
    
    # 返回更新后的日记
    updated_diary = await db.diaries.find_one({"_id": ObjectId(diary_id)})
    updated_diary["id"] = str(updated_diary["_id"])
    del updated_diary["_id"]
    
    return updated_diary

async def delete_diary(diary_id: str, current_user: UserInDB):
    """删除日记"""
    db = get_database()
    
    # 查询日记是否存在
    diary = await db.diaries.find_one({"_id": ObjectId(diary_id), "user_id": str(current_user.id)})
    
    if not diary:
        raise HTTPException(status_code=404, detail="日记不存在或无权访问")
    
    # 删除日记
    await db.diaries.delete_one({"_id": ObjectId(diary_id)})
    
    return {"message": "日记已成功删除"}