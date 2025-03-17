from datetime import datetime, timezone, date
from typing import List, Optional
from fastapi import HTTPException, Depends, Query
from app.config.database import chat_collection, sylus_collection, relationship_collection, get_database
from app.models.user import UserInDB
from app.models.chat import SendMessage, AIResponseRequest, AIResponse, ChatMessage
from app.utils.auth import get_current_active_user
from app.services.ai_service import get_chat_response
from bson import ObjectId

# 获取聊天历史
async def get_chat_history(current_user: UserInDB):
    """获取用户的聊天历史记录"""
    db = get_database()
    
    # 获取用户的聊天历史
    chat_history = await db.chat_messages.find(
        {"user_id": str(current_user.id)}
    ).sort("timestamp", -1).limit(20).to_list(100)
    
    # 转换ObjectId为字符串
    for chat in chat_history:
        chat["id"] = str(chat["_id"])
        del chat["_id"]
    
    return {"messages": chat_history}

# 发送消息
async def send_message(message: ChatMessage, current_user: UserInDB, test_date=None):
    """发送聊天消息"""
    db = get_database()
    
    # 创建新消息
    now = datetime.now()
    new_message = {
        "user_id": str(current_user.id),
        "content": message.content,
        "timestamp": now,
        "type": "user"
    }
    
    # 保存消息到数据库
    insert_result = await db.chat_messages.insert_one(new_message)
    message_id = insert_result.inserted_id
    
    # 检查是否是今天第一次聊天，如果是则增加聊天天数
    today = test_date if test_date else date.today()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    print(f"DEBUG: 检查今天是否有之前的聊天消息, user_id={str(current_user.id)}, today={today}")
    
    # 查询今天发送的第一条消息（不包括刚刚发送的这条）
    today_messages_count = await db.chat_messages.count_documents({
        "user_id": str(current_user.id),
        "timestamp": {"$gte": today_start, "$lt": today_end},
        "_id": {"$ne": message_id}
    })
    
    print(f"DEBUG: 今天之前的聊天消息数量: {today_messages_count}")
    
    # 如果没有今天的其他消息，这是当天第一条消息，则增加聊天天数
    if today_messages_count == 0:
        print("DEBUG: 这是今天第一条消息，增加聊天天数")
        # 使用同步集合更新relationship
        # 获取Sylus ID
        sylus = sylus_collection.find_one()
        if sylus:
            sylus_id = str(sylus["_id"])
            print(f"DEBUG: 找到Sylus, ID={sylus_id}")
            
            # 查找关系信息
            relationship = relationship_collection.find_one({
                "user_id": str(current_user.id),
                "sylus_id": sylus_id
            })
            
            if relationship:
                print(f"DEBUG: 找到关系信息, ID={relationship['_id']}, 当前聊天天数={relationship.get('chat_days', 0)}")
                # 更新聊天天数
                update_result = relationship_collection.update_one(
                    {"_id": relationship["_id"]},
                    {"$inc": {"chat_days": 1}, "$set": {"updated_at": datetime.now(timezone.utc)}}
                )
                print(f"DEBUG: 更新结果: matched={update_result.matched_count}, modified={update_result.modified_count}")
    
    # 返回保存的消息
    saved_message = await db.chat_messages.find_one({"_id": message_id})
    saved_message["id"] = str(saved_message["_id"])
    del saved_message["_id"]
    
    return saved_message

# 获取AI回复
async def get_ai_response(message: ChatMessage, current_user: UserInDB):
    """获取AI对用户消息的回复"""
    db = get_database()
    
    # 创建AI回复消息
    ai_response = {
        "user_id": str(current_user.id),
        "content": f"这是对'{message.content}'的AI回复",
        "timestamp": datetime.now(),
        "type": "ai"
    }
    
    # 保存AI回复到数据库
    result = await db.chat_messages.insert_one(ai_response)
    
    # 返回保存的AI回复
    saved_response = await db.chat_messages.find_one({"_id": result.inserted_id})
    saved_response["id"] = str(saved_response["_id"])
    del saved_response["_id"]
    
    return saved_response 