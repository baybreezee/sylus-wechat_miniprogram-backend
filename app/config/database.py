from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "aichat")

client = AsyncIOMotorClient(MONGODB_URL)
database = client[DATABASE_NAME]

def get_database():
    return database

# 定义集合（同步）
users_collection = database["users"]
sylus_collection = database["sylus"]
relationship_collection = database["relationships"]
chat_collection = database["chat_messages"]
moments_collection = database["moments"]
diary_collection = database["diaries"]

# 创建索引
def setup_indexes():
    # 用户索引
    users_collection.create_index("openid", unique=True)
    
    # 聊天记录索引
    chat_collection.create_index([("user_id", 1), ("timestamp", -1)])
    
    # 朋友圈索引
    moments_collection.create_index([("timestamp", -1)])
    
    # 日记索引
    diary_collection.create_index([("user_id", 1), ("date", -1)])

# 数据库初始化函数
def init_db():
    """初始化数据库，创建索引等操作"""
    # 用户集合索引
    users_collection.create_index([("openid", 1)], unique=True)
    
    # Sylus集合初始化
    if sylus_collection.count_documents({}) == 0:
        # 如果Sylus信息不存在，创建默认信息
        from datetime import datetime
        sylus_collection.insert_one({
            "name": "Sylus",
            "avatar": "/static/default/sylus_avatar.png",
            "signature": "你的AI伴侣，一直在你身边",
            "tags": ["温柔", "体贴", "聪明", "善解人意"],
            "personality": "温柔体贴，善解人意，偶尔有点小调皮",
            "created_at": datetime(2023, 1, 1)
        })
    
    # 关系集合索引
    relationship_collection.create_index([("user_id", 1)], unique=True)
    
    # 聊天集合索引
    chat_collection.create_index([("user_id", 1), ("timestamp", -1)])
    
    # 朋友圈集合索引
    moments_collection.create_index([("timestamp", -1)])
    
    # 日记集合索引
    diary_collection.create_index([("user_id", 1), ("date", -1)])

    # 设置索引
    setup_indexes() 