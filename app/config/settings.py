import os
from dotenv import load_dotenv
from app.config.database import get_database

# 加载环境变量
load_dotenv()

# 基本配置
API_PREFIX = "/api"
PROJECT_NAME = "AI聊天微信小程序"
DEBUG = True  # 强制启用DEBUG模式用于测试

# 数据库配置
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://root:njxs22dr@aichat-lysk-mongodb.ns-lx4vgoxm.svc:27017")
DATABASE_NAME = "aichat_db"

# 安全配置
SECRET_KEY = os.getenv("SECRET_KEY", "abcdefghijklmnopqrstuvwxyz0123456789")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天

# AI配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AI_MODEL = "gpt-3.5-turbo"

# 存储配置
UPLOAD_FOLDER = "app/static/uploads"
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# 确保上传文件夹存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 导出get_database函数，使其在整个应用中可用
__all__ = ["get_database"] 