from typing import List, Optional, Dict, Any
from pydantic import BaseModel

# 情感分析请求模型
class EmotionAnalysisRequest(BaseModel):
    text: str
    user_id: Optional[str] = None

# 情感分析响应模型
class EmotionAnalysisResponse(BaseModel):
    emotion: str
    confidence: float
    details: Dict[str, Any] = {}

# 个性化回复请求模型
class PersonalizedResponseRequest(BaseModel):
    user_id: str
    message: str
    context: Optional[List[Dict[str, Any]]] = None

# 个性化回复响应模型
class PersonalizedResponseResponse(BaseModel):
    response: str
    emotion: Optional[str] = None
    suggested_actions: Optional[List[str]] = None 