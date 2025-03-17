from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel, Field
from enum import Enum

# 日记基本模型
class DiaryBase(BaseModel):
    user_id: str
    author_name: str
    author_type: str  # "user" 或 "sylus"
    content: str
    mood: Optional[str] = None
    images: List[str] = []
    date: Optional[date] = None
    timestamp: Optional[datetime] = None

# 日记响应模型
class Diary(DiaryBase):
    id: str = Field(alias="_id")

    class Config:
        allow_population_by_field_name = True
        orm_mode = True

class MoodEnum(str, Enum):
    """心情枚举"""
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    EXCITED = "excited"
    CALM = "calm"
    ANXIOUS = "anxious"
    NEUTRAL = "neutral"

class DiaryCreate(BaseModel):
    """创建日记模型"""
    title: str
    content: str
    mood: Optional[MoodEnum] = None
    date: Optional[date] = None

class DiaryUpdate(BaseModel):
    """更新日记模型"""
    title: Optional[str] = None
    content: Optional[str] = None
    mood: Optional[MoodEnum] = None
    date: Optional[date] = None

# 创建日记请求模型
class CreateDiary(BaseModel):
    """创建日记请求模型"""
    content: str
    mood: Optional[str] = None
    images: List[str] = []

# AI日记响应请求模型
class DiaryAIResponseRequest(BaseModel):
    """请求AI日记回应的模型"""
    diary_id: str

# 日记列表请求模型
class DiaryListRequest(BaseModel):
    limit: int = 10
    before_date: Optional[date] = None 