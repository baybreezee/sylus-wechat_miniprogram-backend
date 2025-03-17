import requests
import json
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from bson import ObjectId
from app.config.database import users_collection
from app.models.user import UserLogin, UserCreate, UserInDB
from app.utils.auth import create_access_token, get_password_hash, Token
from app.config.settings import ACCESS_TOKEN_EXPIRE_MINUTES, DEBUG

# 微信小程序登录
async def wechat_login(login_data: UserLogin):
    # 测试模式：如果在DEBUG模式下，直接使用测试code登录，跳过微信API调用
    if DEBUG:
        # 使用code后六位作为测试用户标识
        test_openid = f"test_openid_{login_data.code[-6:]}"
        
        # 检查测试用户是否已存在
        user = users_collection.find_one({"openid": test_openid})
        
        # 如果测试用户不存在，创建新测试用户
        if not user:
            now = datetime.utcnow()
            new_user = {
                "openid": test_openid,
                "nickname": f"测试用户{test_openid[-6:]}",  # 使用测试openid的最后6位作为默认昵称
                "avatar": "/static/default/avatar.png",  # 默认头像
                "signature": "这是一个测试账号",
                "tags": ["测试"],
                "hashed_password": get_password_hash(test_openid),  # 使用openid作为初始密码
                "disabled": False,
                "created_at": now,
                "updated_at": now
            }
            
            result = users_collection.insert_one(new_user)
            user = users_collection.find_one({"_id": result.inserted_id})
        
        # 确保_id是字符串类型
        if "_id" in user and isinstance(user["_id"], ObjectId):
            user["_id"] = str(user["_id"])
            
        # 创建访问令牌
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": test_openid}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_info": {
                "id": str(user["_id"]),
                "openid": user["openid"],
                "nickname": user.get("nickname"),
                "avatar": user.get("avatar"),
                "signature": user.get("signature"),
                "tags": user.get("tags", [])
            }
        }
    
    # 正常微信登录流程（非DEBUG模式）
    # 微信小程序登录配置
    # 注意：实际应用中，这些值应该从环境变量或配置文件中获取
    appid = "your_appid"  # 替换为实际的小程序appid
    secret = "your_secret"  # 替换为实际的小程序secret
    
    # 请求微信API获取openid
    url = f"https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={login_data.code}&grant_type=authorization_code"
    response = requests.get(url)
    
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="微信登录失败")
    
    data = response.json()
    
    if "errcode" in data and data["errcode"] != 0:
        raise HTTPException(status_code=400, detail=f"微信登录错误: {data.get('errmsg', '未知错误')}")
    
    openid = data.get("openid")
    if not openid:
        raise HTTPException(status_code=400, detail="获取openid失败")
    
    # 检查用户是否已存在
    user = users_collection.find_one({"openid": openid})
    
    # 如果用户不存在，创建新用户
    if not user:
        now = datetime.utcnow()
        new_user = {
            "openid": openid,
            "nickname": f"用户{openid[-6:]}",  # 使用openid的最后6位作为默认昵称
            "avatar": "/static/default/avatar.png",  # 默认头像
            "signature": "这个人很懒，什么都没留下",
            "tags": [],
            "hashed_password": get_password_hash(openid),  # 使用openid作为初始密码
            "disabled": False,
            "created_at": now,
            "updated_at": now
        }
        
        result = users_collection.insert_one(new_user)
        user = users_collection.find_one({"_id": result.inserted_id})
    
    # 确保_id是字符串类型
    if "_id" in user and isinstance(user["_id"], ObjectId):
        user["_id"] = str(user["_id"])
        
    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": openid}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_info": {
            "id": str(user["_id"]),
            "openid": user["openid"],
            "nickname": user.get("nickname"),
            "avatar": user.get("avatar"),
            "signature": user.get("signature"),
            "tags": user.get("tags", [])
        }
    }

# 获取访问令牌（用于测试）
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # 在实际的微信小程序中，这个接口可能不会被使用
    # 这里主要用于开发测试
    
    # 查找用户
    user = users_collection.find_one({"openid": form_data.username})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer") 