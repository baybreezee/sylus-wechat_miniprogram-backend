from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

# 消息基本模型
class MessageBase(BaseModel):
    user_id: str
    sender_type: str  # "user" 或 "sylus"
    content: str
    content_type: str = "text"  # "text", "image", "voice", "video"
    media_url: Optional[str] = None
    timestamp: datetime = datetime.utcnow()

# 消息响应模型
class Message(MessageBase):
    id: str = Field(alias="_id")

    class Config:
        allow_population_by_field_name = True
        orm_mode = True

# 发送消息请求模型
class SendMessage(BaseModel):
    content: str
    content_type: str = "text"
    media_url: Optional[str] = None

# AI响应请求模型
class AIResponseRequest(BaseModel):
    message_id: str

# AI响应结果模型
class AIResponse(BaseModel):
    response: str
    emotion: str = "neutral"

# 聊天历史请求模型
class ChatHistoryRequest(BaseModel):
    limit: int = 20
    before_timestamp: Optional[datetime] = None

class ChatMessage(BaseModel):
    """聊天消息模型"""
    content: str 