import uvicorn
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

if __name__ == "__main__":
    # 获取环境变量或使用默认值
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "2100"))
    reload = os.getenv("RELOAD", "False").lower() == "true"
    
    # 启动服务器
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload
    ) 