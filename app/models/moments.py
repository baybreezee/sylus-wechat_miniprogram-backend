from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

# 评论模型
class Comment(BaseModel):
    id: str
    user_id: Optional[str] = None
    author_name: str
    author_avatar: Optional[str] = None
    is_sylus: bool = False
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# 点赞模型
class Like(BaseModel):
    user_id: Optional[str] = None
    name: str
    avatar: Optional[str] = None
    is_sylus: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# 朋友圈基本模型
class MomentBase(BaseModel):
    user_id: str
    author_name: str
    author_avatar: Optional[str] = None
    content: str
    images: List[str] = []
    location: Optional[str] = None
    likes: List[Like] = []
    comments: List[Comment] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# 朋友圈响应模型
class Moment(MomentBase):
    id: str = Field(alias="_id")

    class Config:
        allow_population_by_field_name = True
        orm_mode = True

# 创建朋友圈请求模型
class CreateMoment(BaseModel):
    content: str
    images: List[str] = []
    location: Optional[str] = None

# 评论请求模型
class CreateComment(BaseModel):
    content: str

# AI朋友圈响应请求模型
class MomentAIResponseRequest(BaseModel):
    moment_id: str

# 朋友圈列表请求模型
class MomentsListRequest(BaseModel):
    limit: int = 10
    before_timestamp: Optional[datetime] = None 