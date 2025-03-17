from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

# 关系基本模型
class RelationshipBase(BaseModel):
    user_id: str
    sylus_id: str
    start_date: datetime
    sweetness: int = 0
    level: int = 1
    chat_days: int = 0
    milestones: List[dict] = []

# 关系响应模型
class Relationship(RelationshipBase):
    id: str = Field(alias="_id")
    days_together: int
    created_at: datetime
    updated_at: datetime

    class Config:
        allow_population_by_field_name = True
        orm_mode = True

# 更新关系请求模型
class RelationshipUpdate(BaseModel):
    sweetness_delta: Optional[int] = None 