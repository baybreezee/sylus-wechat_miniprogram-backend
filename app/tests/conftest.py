import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config.database import users_collection, sylus_collection
from app.utils.auth import create_access_token
from datetime import datetime, timedelta
import os
import json

# 测试客户端
@pytest.fixture
def client():
    return TestClient(app)

# 测试用户数据
@pytest.fixture
def test_user_data():
    return {
        "openid": "test_openid",
        "nickname": "测试用户",
        "avatar": "/static/default/avatar.png",
        "signature": "这是一个测试签名",
        "tags": ["测试", "用户"],
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # 密码: test_openid
        "disabled": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

# 创建测试用户并返回token
@pytest.fixture
def test_user_token(test_user_data):
    # 清理可能存在的测试用户
    users_collection.delete_many({"openid": test_user_data["openid"]})
    
    # 创建测试用户
    users_collection.insert_one(test_user_data)
    
    # 创建访问令牌
    access_token = create_access_token(
        data={"sub": test_user_data["openid"]},
        expires_delta=timedelta(minutes=30)
    )
    
    return access_token

# 测试Sylus数据
@pytest.fixture
def test_sylus_data():
    return {
        "name": "Sylus",
        "avatar": "/static/default/sylus_avatar.png",
        "signature": "你的AI伴侣，一直在你身边",
        "tags": ["温柔", "体贴", "聪明", "善解人意"],
        "personality": "温柔体贴，善解人意，偶尔有点小调皮",
        "created_at": datetime.utcnow()
    }

# 创建测试Sylus
@pytest.fixture
def test_sylus(test_sylus_data):
    # 清理可能存在的测试Sylus
    sylus_collection.delete_many({"name": test_sylus_data["name"]})
    
    # 创建测试Sylus
    result = sylus_collection.insert_one(test_sylus_data)
    
    # 返回ID
    return str(result.inserted_id)

# 带认证的请求头
@pytest.fixture
def auth_headers(test_user_token):
    return {"Authorization": f"Bearer {test_user_token}"}