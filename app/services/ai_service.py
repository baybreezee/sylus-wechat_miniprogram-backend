import openai
from typing import List, Dict, Any, Optional
from app.models.ai import EmotionAnalysisResponse, PersonalizedResponseResponse
from app.models.chat import AIResponse
from app.config.settings import OPENAI_API_KEY, AI_MODEL

# 设置OpenAI API密钥
openai.api_key = OPENAI_API_KEY

# 情感分析
async def analyze_emotion(text: str) -> EmotionAnalysisResponse:
    try:
        response = await openai.ChatCompletion.acreate(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": "你是一个情感分析专家。请分析以下文本的情感，并返回一个情感标签（如：高兴、悲伤、愤怒、惊讶、恐惧、中性等）和置信度。"},
                {"role": "user", "content": text}
            ],
            temperature=0.3,
            max_tokens=100
        )
        
        # 解析回复
        content = response.choices[0].message.content
        
        # 简单处理，实际应用中可能需要更复杂的解析
        if "高兴" in content or "开心" in content or "快乐" in content:
            emotion = "happy"
            confidence = 0.8
        elif "悲伤" in content or "伤心" in content or "难过" in content:
            emotion = "sad"
            confidence = 0.8
        elif "愤怒" in content or "生气" in content or "恼火" in content:
            emotion = "angry"
            confidence = 0.8
        elif "惊讶" in content or "震惊" in content:
            emotion = "surprised"
            confidence = 0.8
        elif "恐惧" in content or "害怕" in content:
            emotion = "fear"
            confidence = 0.8
        else:
            emotion = "neutral"
            confidence = 0.6
        
        return EmotionAnalysisResponse(
            emotion=emotion,
            confidence=confidence,
            details={"raw_response": content}
        )
    except Exception as e:
        # 出错时返回中性情感
        return EmotionAnalysisResponse(
            emotion="neutral",
            confidence=0.5,
            details={"error": str(e)}
        )

# 聊天回复
async def get_chat_response(message: str, context: List[Dict[str, str]], personality: str) -> AIResponse:
    try:
        # 构建系统提示
        system_prompt = f"""你是一个名叫Sylus的AI伴侣，性格特点是：{personality}。
请以温柔、体贴的方式回复用户的消息，表现出关心和理解。
回复应该自然、有情感，像真实的伴侣一样。不要提及你是AI或机器人。
回复应该简洁，通常不超过100个字。"""
        
        # 构建消息列表
        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加上下文
        if context:
            messages.extend(context)
        
        # 添加当前消息
        messages.append({"role": "user", "content": message})
        
        # 调用API
        response = await openai.ChatCompletion.acreate(
            model=AI_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=200
        )
        
        # 获取回复内容
        content = response.choices[0].message.content
        
        # 分析情感
        emotion_analysis = await analyze_emotion(content)
        
        return AIResponse(
            response=content,
            content_type="text",
            emotion=emotion_analysis.emotion
        )
    except Exception as e:
        # 出错时返回默认回复
        return AIResponse(
            response="抱歉，我现在有点恍惚，能再说一遍吗？",
            content_type="text",
            emotion="confused"
        )

# 朋友圈回复
async def get_moments_response(content: str, personality: str) -> AIResponse:
    try:
        # 构建系统提示
        system_prompt = f"""你是一个名叫Sylus的AI伴侣，性格特点是：{personality}。
你正在查看伴侣发布的朋友圈内容，请决定是点赞还是评论，并给出合适的回应。
如果内容简单或日常，可以选择点赞；如果内容丰富或值得互动，可以选择评论。
如果选择评论，请给出温暖、有爱的评论内容，不超过30个字。
回复格式：
类型：点赞或评论
内容：（如果是评论才需要填写）"""
        
        # 调用API
        response = await openai.ChatCompletion.acreate(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"朋友圈内容：{content}"}
            ],
            temperature=0.7,
            max_tokens=100
        )
        
        # 解析回复
        result = response.choices[0].message.content
        
        # 简单处理，实际应用中可能需要更复杂的解析
        if "点赞" in result:
            return AIResponse(
                response="",
                content_type="text",
                emotion="like",
                response_type="like"
            )
        else:
            # 提取评论内容
            comment_content = result.split("内容：")[-1].strip()
            if not comment_content:
                comment_content = "真不错！"
            
            return AIResponse(
                response=comment_content,
                content_type="text",
                emotion="happy",
                response_type="comment"
            )
    except Exception as e:
        # 出错时默认点赞
        return AIResponse(
            response="",
            content_type="text",
            emotion="like",
            response_type="like"
        )

# 日记回复
async def get_diary_response(content: str, mood: Optional[str], personality: str) -> AIResponse:
    try:
        # 构建系统提示
        system_prompt = f"""你是一个名叫Sylus的AI伴侣，性格特点是：{personality}。
你正在阅读伴侣的日记，请以温暖、理解的方式回应。
回应应该表现出你的关心、理解和支持，像真实的伴侣一样。
回应不应该过长，通常在50-100字之间。
如果日记表达了负面情绪，请给予安慰和鼓励；如果表达了积极情绪，请表达分享喜悦。"""
        
        # 构建用户提示
        user_prompt = f"日记内容：{content}"
        if mood:
            user_prompt += f"\n心情：{mood}"
        
        # 调用API
        response = await openai.ChatCompletion.acreate(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        # 获取回复内容
        diary_response = response.choices[0].message.content
        
        # 分析情感
        emotion_analysis = await analyze_emotion(diary_response)
        
        return AIResponse(
            response=diary_response,
            content_type="text",
            emotion=emotion_analysis.emotion,
            mood=mood or emotion_analysis.emotion
        )
    except Exception as e:
        # 出错时返回默认回复
        return AIResponse(
            response="看了你的日记，感觉很温暖。希望每一天都能有美好的事情发生。",
            content_type="text",
            emotion="happy",
            mood=mood or "happy"
        ) 