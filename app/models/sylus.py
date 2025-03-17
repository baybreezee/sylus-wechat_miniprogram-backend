from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

# Sylus基本模型
class SylusBase(BaseModel):
    name: str
    avatar: str
    signature: str
    tags: List[str]
    personality: str

# Sylus响应模型
class Sylus(SylusBase):
    id: str = Field(alias="_id")
    created_at: datetime

    class Config:
        allow_population_by_field_name = True
        orm_mode = True 