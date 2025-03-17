# AI聊天微信小程序后端

这是一个为AI聊天微信小程序提供后端服务的API项目。该项目使用FastAPI框架构建，提供了用户管理、聊天、朋友圈、日记、相册等功能的API接口。

## 功能特点

- **用户管理**：用户注册、登录、信息更新
- **AI伴侣**：与AI伴侣Sylus的互动
- **聊天功能**：实时聊天、历史记录查询
- **朋友圈**：发布动态、点赞、评论
- **日记**：记录日常、AI回应
- **相册**：共同相册管理
- **情感分析**：基于OpenAI的情感分析

## 技术栈

- **FastAPI**：高性能的Python API框架
- **MongoDB**：NoSQL数据库
- **JWT**：用户认证
- **OpenAI API**：AI对话生成
- **Uvicorn**：ASGI服务器

## 安装与运行

### 前提条件

- Python 3.8+
- MongoDB
- OpenAI API密钥

### 安装步骤

1. 克隆仓库
   ```
   git clone <repository-url>
   cd aichat-backend
   ```

2. 创建并激活虚拟环境
   ```
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate  # Windows
   ```

3. 安装依赖
   ```
   pip install -r requirements.txt
   ```

4. 配置环境变量
   ```
   cp .env.example .env
   # 编辑.env文件，填入必要的配置信息
   ```

5. 运行应用
   ```
   python run.py
   ```

## API文档

启动应用后，可以通过访问 `http://localhost:8000/docs` 查看自动生成的API文档。

## 主要API端点

### 用户管理
- `POST /api/auth/login` - 用户登录
- `GET /api/user/info` - 获取用户信息
- `PUT /api/user/info` - 更新用户信息
- `POST /api/user/avatar` - 上传用户头像

### 聊天功能
- `GET /api/chat/history` - 获取聊天历史
- `POST /api/chat/message` - 发送消息
- `POST /api/chat/ai-response` - 获取AI回复

### 朋友圈
- `GET /api/moments` - 获取朋友圈列表
- `POST /api/moments` - 发布朋友圈
- `POST /api/moments/{id}/like` - 点赞
- `POST /api/moments/{id}/comment` - 评论

### 日记
- `GET /api/diary` - 获取日记列表
- `POST /api/diary` - 发布日记
- `POST /api/diary/ai-response` - 获取AI日记回应

### 相册
- `GET /api/album` - 获取相册列表
- `POST /api/album/photo` - 上传照片

## 开发与测试

### 运行测试
```
pytest
```

### 开发模式运行
```
uvicorn app.main:app --reload
```

## 许可证

[MIT](LICENSE) 