from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import MONGODB_URL, DATABASE_NAME

# 创建MongoDB客户端连接（同步）
client = MongoClient(MONGODB_URL)
db = client[DATABASE_NAME]

# 创建MongoDB客户端连接（异步）
async_client = AsyncIOMotorClient(MONGODB_URL)
async_db = async_client[DATABASE_NAME]

# 定义集合（同步）
users_collection = db["users"]
sylus_collection = db["sylus"]
relationship_collection = db["relationships"]
chat_collection = db["chat_messages"]
moments_collection = db["moments"]
diary_collection = db["diaries"]
album_collection = db["albums"]

# 获取异步数据库
def get_database():
    """获取异步数据库连接"""
    return async_db

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
    
    # 相册索引
    album_collection.create_index([("upload_date", -1)])

# 数据库初始化函数
def init_db():
    # 设置索引
    setup_indexes()
    
    # 如果Sylus信息不存在，则初始化
    if sylus_collection.count_documents({}) == 0:
        sylus_info = {
            "name": "Sylus",
            "avatar": "/static/default/sylus_avatar.png",
            "signature": "你的AI伴侣，一直在你身边",
            "tags": ["温柔", "体贴", "聪明", "善解人意"],
            "personality": "温柔体贴，善解人意，偶尔有点小调皮",
            "created_at": "2023-01-01T00:00:00Z"
        }
        sylus_collection.insert_one(sylus_info) 