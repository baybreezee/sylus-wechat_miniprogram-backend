from fastapi import APIRouter, Depends
from app.controllers.chat_controller import get_chat_history, send_message, get_ai_response
from app.models.user import UserInDB
from app.models.chat import ChatMessage
from app.utils.auth import get_current_active_user
from datetime import date, timedelta

router = APIRouter(prefix="/api/chat", tags=["聊天"])

@router.get("/history")
async def chat_history(current_user: UserInDB = Depends(get_current_active_user)):
    """获取用户的聊天历史记录"""
    return await get_chat_history(current_user)

@router.post("/send")
async def send_chat_message(message: ChatMessage, current_user: UserInDB = Depends(get_current_active_user)):
    """发送聊天消息"""
    return await send_message(message, current_user)

@router.post("/ai_response")
async def ai_response(message: ChatMessage, current_user: UserInDB = Depends(get_current_active_user)):
    """获取AI对用户消息的回复"""
    return await get_ai_response(message, current_user)

@router.post("/test_new_day")
async def test_new_day(message: ChatMessage, current_user: UserInDB = Depends(get_current_active_user)):
    """测试新的一天发送消息（增加聊天天数）"""
    # 使用明天的日期作为测试日期
    tomorrow = date.today() + timedelta(days=1)
    return await send_message(message, current_user, test_date=tomorrow) 