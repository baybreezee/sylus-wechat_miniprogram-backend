import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import openai
from app.config.settings import AI_MODEL, OPENAI_API_KEY
from app.config.database import get_database, chat_collection
from app.models.chat import AIResponse

# 设置OpenAI API密钥
openai.api_key = OPENAI_API_KEY

class MemoryService:
    """自定义记忆管理服务，提供类似Letta的功能"""
    
    def __init__(self, user_id: str, max_tokens: int = 2000, max_messages: int = 20):
        self.user_id = user_id
        self.max_tokens = max_tokens  # 上下文最大token数
        self.max_messages = max_messages  # 最大消息数量
        self.db = get_database()
    
    async def get_recent_messages(self, limit: int = None) -> List[Dict[str, Any]]:
        """获取最近的聊天记录"""
        if limit is None:
            limit = self.max_messages
            
        # 从数据库获取最近的消息
        messages = await self.db.chat_messages.find(
            {"user_id": self.user_id}
        ).sort("timestamp", -1).limit(limit).to_list(length=limit)
        
        # 按时间顺序排列
        messages.reverse()
        
        return messages
    
    async def generate_summary(self, messages: List[Dict[str, Any]]) -> str:
        """生成聊天记录的摘要"""
        if not messages:
            return ""
        
        # 将消息格式化为文本
        formatted_messages = []
        for msg in messages:
            role = "用户" if msg.get("type") == "user" else "Sylus"
            formatted_messages.append(f"{role}: {msg.get('content', '')}")
        
        chat_history = "\n".join(formatted_messages)
        
        try:
            # 使用OpenAI生成摘要
            response = await openai.ChatCompletion.acreate(
                model=AI_MODEL,
                messages=[
                    {"role": "system", "content": "你是一个专业的对话摘要生成器。请将以下对话内容总结为一段简短的摘要，保留关键信息和情感表达。摘要应不超过100个字。"},
                    {"role": "user", "content": f"请总结以下对话：\n\n{chat_history}"}
                ],
                temperature=0.3,
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"生成摘要时出错: {str(e)}")
            # 简单地返回最后几条消息
            return chat_history[-100:] if len(chat_history) > 100 else chat_history
    
    async def extract_key_info(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """从聊天记录中提取关键信息"""
        if not messages:
            return {}
        
        # 将消息格式化为文本
        chat_history = []
        for msg in messages:
            role = "用户" if msg.get("type") == "user" else "Sylus" 
            chat_history.append(f"{role}: {msg.get('content', '')}")
        
        chat_text = "\n".join(chat_history)
        
        try:
            # 使用OpenAI提取关键信息
            response = await openai.ChatCompletion.acreate(
                model=AI_MODEL,
                messages=[
                    {"role": "system", "content": """你是一个专业的信息提取专家。请从以下对话中提取关键信息，并以JSON格式返回。
                    请提取以下信息（如果存在）：
                    1. 用户的兴趣爱好
                    2. 用户的情感状态
                    3. 重要的事件或约定
                    4. 用户提到的人名
                    5. 用户的偏好
                    
                    JSON格式如下：
                    {
                      "interests": ["兴趣1", "兴趣2"],
                      "emotional_state": "情感状态",
                      "events": ["事件1", "事件2"],
                      "people": ["人名1", "人名2"],
                      "preferences": ["偏好1", "偏好2"]
                    }
                    
                    如果某项信息不存在，请使用空列表或空字符串。"""},
                    {"role": "user", "content": f"请从以下对话中提取关键信息：\n\n{chat_text}"}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            # 解析JSON
            content = response.choices[0].message.content.strip()
            try:
                # 尝试直接解析
                return json.loads(content)
            except json.JSONDecodeError:
                # 尝试从文本中提取JSON部分
                import re
                json_match = re.search(r'({.*})', content, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group(1))
                    except:
                        pass
                
                # 失败时返回空字典
                return {}
        except Exception as e:
            print(f"提取关键信息时出错: {str(e)}")
            return {}
    
    async def compress_context(self, messages: List[Dict[str, Any]], target_length: int = None) -> List[Dict[str, Any]]:
        """压缩对话上下文至目标长度"""
        if target_length is None:
            target_length = self.max_messages // 2
        
        if len(messages) <= target_length:
            return messages
        
        # 保留最近的几条消息
        recent_count = min(5, target_length // 2)
        recent_messages = messages[-recent_count:]
        
        # 为其余消息生成摘要
        summary_messages = messages[:-recent_count]
        summary = await self.generate_summary(summary_messages)
        
        # 创建一个系统消息来包含摘要
        summary_message = {
            "user_id": self.user_id,
            "content": f"[之前对话摘要] {summary}",
            "timestamp": datetime.now(),
            "type": "system"
        }
        
        # 组合摘要和最近消息
        return [summary_message] + recent_messages
    
    async def get_formatted_context(self, personality: str = "") -> List[Dict[str, str]]:
        """获取格式化的上下文，用于AI模型输入"""
        # 获取最近消息
        messages = await self.get_recent_messages()
        
        # 如果消息超过阈值，进行压缩
        if len(messages) > self.max_messages:
            messages = await self.compress_context(messages)
        
        # 提取关键信息
        key_info = await self.extract_key_info(messages)
        
        # 格式化为OpenAI API的消息格式
        formatted_messages = []
        
        # 添加一个系统消息，包含关键信息
        if key_info:
            key_info_str = json.dumps(key_info, ensure_ascii=False)
            formatted_messages.append({
                "role": "system", 
                "content": f"以下是从之前对话中提取的关键信息，请在回复中适当利用:\n{key_info_str}"
            })
        
        # 添加聊天记录
        for msg in messages:
            role = "user" if msg.get("type") == "user" else "assistant"
            if msg.get("type") == "system":
                continue  # 跳过系统消息，因为我们已经添加了关键信息
                
            formatted_messages.append({
                "role": role,
                "content": msg.get("content", "")
            })
        
        return formatted_messages
    
    async def save_message(self, message: Dict[str, Any]):
        """保存消息到数据库"""
        await self.db.chat_messages.insert_one(message)
    
    async def save_conversation_summary(self):
        """生成并保存对话摘要"""
        messages = await self.get_recent_messages(50)  # 获取最近50条消息
        summary = await self.generate_summary(messages)
        
        # 保存摘要到数据库
        await self.db.conversation_summaries.update_one(
            {"user_id": self.user_id},
            {"$set": {
                "user_id": self.user_id,
                "summary": summary,
                "created_at": datetime.now()
            }},
            upsert=True
        )
        
        return summary

# 工厂函数，方便创建记忆服务实例
async def get_memory_service(user_id: str) -> MemoryService:
    """创建并返回记忆服务实例"""
    return MemoryService(user_id=user_id) 