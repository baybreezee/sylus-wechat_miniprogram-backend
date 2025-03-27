import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 基础配置
API_PREFIX = "/api"
PROJECT_NAME = "AI Chat Backend"
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# 安全配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# AI配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AI_MODEL = "gpt-3.5-turbo"

# 存储配置
UPLOAD_FOLDER = "uploads"
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# 确保上传文件夹存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 导出配置
__all__ = [
    "API_PREFIX",
    "PROJECT_NAME",
    "DEBUG",
    "SECRET_KEY",
    "ALGORITHM",
    "ACCESS_TOKEN_EXPIRE_MINUTES",
    "OPENAI_API_KEY",
    "AI_MODEL",
    "UPLOAD_FOLDER",
    "MAX_CONTENT_LENGTH"
] 