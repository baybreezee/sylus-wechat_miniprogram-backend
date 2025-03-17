from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

# 用户基本模型
class UserBase(BaseModel):
    openid: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    signature: Optional[str] = None
    tags: List[str] = []

# 创建用户请求模型
class UserCreate(UserBase):
    password: str

# 用户响应模型
class User(UserBase):
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime

    class Config:
        allow_population_by_field_name = True
        orm_mode = True

# 数据库中的用户模型
class UserInDB(UserBase):
    id: Optional[str] = Field(None, alias="_id")
    hashed_password: str
    disabled: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        allow_population_by_field_name = True
        orm_mode = True

# 更新用户信息请求模型
class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    signature: Optional[str] = None
    tags: Optional[List[str]] = None

# 用户登录请求模型
class UserLogin(BaseModel):
    code: str  # 微信小程序登录时获取的code

# 用户头像上传响应
class UserAvatarResponse(BaseModel):
    avatar_url: str 