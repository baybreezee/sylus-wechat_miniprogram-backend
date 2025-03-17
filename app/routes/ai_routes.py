from fastapi import APIRouter, Depends
from app.services.ai_service import analyze_emotion
from app.models.user import UserInDB
from app.models.ai import EmotionAnalysisRequest, PersonalizedResponseRequest
from app.utils.auth import get_current_active_user

router = APIRouter(prefix="/api/ai", tags=["AI"])

@router.post("/emotion-analysis")
async def emotion_analysis(
    request: EmotionAnalysisRequest,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """分析用户消息情感"""
    return await analyze_emotion(request.text) 