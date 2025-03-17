from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os

from app.config.settings import API_PREFIX, PROJECT_NAME, DEBUG
from app.config.database import init_db

# 导入路由
from app.routes import (
    user_routes, sylus_routes, relationship_routes,
    chat_routes, moments_routes, diary_routes,
    album_routes, auth_routes, ai_routes
)

# 创建应用
app = FastAPI(
    title=PROJECT_NAME,
    description="AI聊天微信小程序后端API",
    version="1.0.0",
    debug=DEBUG
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(sylus_routes.router)
app.include_router(relationship_routes.router)
app.include_router(chat_routes.router)
app.include_router(moments_routes.router)
app.include_router(diary_routes.router)
app.include_router(album_routes.router)
app.include_router(ai_routes.router)

# 配置静态文件
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if DEBUG:
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc), "type": str(type(exc).__name__)},
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"detail": "服务器内部错误"},
        )

# 启动事件
@app.on_event("startup")
async def startup_event():
    # 初始化数据库
    init_db()
    
    # 确保静态文件目录存在
    os.makedirs("app/static/default", exist_ok=True)
    os.makedirs("app/static/uploads", exist_ok=True)

# 根路由
@app.get("/")
async def root():
    return {"message": f"欢迎使用{PROJECT_NAME}后端API", "version": "1.0.0"} 