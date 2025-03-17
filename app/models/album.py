from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

# 照片基本模型
class PhotoBase(BaseModel):
    user_id: str
    uploader_name: str
    uploader_type: str  # "user" 或 "sylus"
    image_url: str
    caption: Optional[str] = None
    location: Optional[str] = None
    upload_date: datetime = Field(default_factory=datetime.utcnow)

# 照片响应模型
class Photo(PhotoBase):
    id: str = Field(alias="_id")

    class Config:
        allow_population_by_field_name = True
        orm_mode = True

# 上传照片请求模型
class UploadPhoto(BaseModel):
    caption: Optional[str] = None
    location: Optional[str] = None

# 相册列表请求模型
class AlbumListRequest(BaseModel):
    limit: int = 20
    before_date: Optional[datetime] = None 