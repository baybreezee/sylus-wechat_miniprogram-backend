import pytest
from fastapi.testclient import TestClient
import json

# 测试获取用户信息
def test_get_user_info(client, auth_headers, test_user_data):
    response = client.get("/api/user/info", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["openid"] == test_user_data["openid"]
    assert data["nickname"] == test_user_data["nickname"]
    assert data["signature"] == test_user_data["signature"]
    assert data["tags"] == test_user_data["tags"]

# 测试更新用户信息
def test_update_user_info(client, auth_headers):
    update_data = {
        "nickname": "更新后的昵称",
        "signature": "更新后的签名",
        "tags": ["新标签1", "新标签2"]
    }
    
    response = client.put(
        "/api/user/info",
        headers=auth_headers,
        json=update_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["nickname"] == update_data["nickname"]
    assert data["signature"] == update_data["signature"]
    assert data["tags"] == update_data["tags"]

# 测试未授权访问
def test_unauthorized_access(client):
    response = client.get("/api/user/info")
    assert response.status_code == 401 