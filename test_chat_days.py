import requests
import json
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:2100"

def test_login():
    """测试用户登录"""
    print("\n==================================================")
    print("  测试用户登录")
    print("==================================================")
    
    url = f"{BASE_URL}/api/users/login"
    data = {
        "code": "0e1yGX0w3uSry434cC0w3NyK751yGX0i"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"\n【用户登录】状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"✅ 登录成功，获取到token: {token[:10]}...")
            return token
        else:
            print(f"❌ 登录失败: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 登录请求异常: {str(e)}")
        # 使用模拟token继续测试
        print("将使用模拟token继续测试其他接口")
        return "mock_token"

def test_get_relationship(token):
    """测试获取与Sylus的关系"""
    print("\n==================================================")
    print("  测试获取与Sylus的关系")
    print("==================================================")
    
    url = f"{BASE_URL}/api/relationship/status"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        print(f"\n【获取与Sylus的关系】状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return None

def test_send_message(token):
    """测试发送消息"""
    print("\n==================================================")
    print("  测试发送消息")
    print("==================================================")
    
    url = f"{BASE_URL}/api/chat/send"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "content": f"这是一条测试消息 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"\n【发送消息】状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            message_id = response.json().get("id")
            print(f"✅ 发送成功，消息ID: {message_id}")
            return message_id
        else:
            print(f"❌ 发送失败: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return None

def test_new_day_message(token):
    """测试新的一天发送消息（增加聊天天数）"""
    print("\n==================================================")
    print("  测试新的一天发送消息（增加聊天天数）")
    print("==================================================")
    
    url = f"{BASE_URL}/api/chat/test_new_day"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "content": f"这是一条新的一天的测试消息 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"\n【新的一天发送消息】状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            message_id = response.json().get("id")
            print(f"✅ 发送成功，消息ID: {message_id}")
            return message_id
        else:
            print(f"❌ 发送失败: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return None

if __name__ == "__main__":
    # 测试登录
    token = test_login()
    
    if token:
        # 获取初始关系信息
        print("\n初始关系信息:")
        initial_relationship = test_get_relationship(token)
        
        # 发送普通消息
        test_send_message(token)
        
        # 再次获取关系信息，确认聊天天数没有变化
        print("\n发送普通消息后的关系信息:")
        after_normal_message = test_get_relationship(token)
        
        # 发送新的一天的消息
        test_new_day_message(token)
        
        # 再次获取关系信息，确认聊天天数增加了
        print("\n发送新的一天消息后的关系信息:")
        after_new_day = test_get_relationship(token)
        
        # 打印聊天天数变化
        if initial_relationship and after_normal_message and after_new_day:
            print("\n==================================================")
            print("  聊天天数变化")
            print("==================================================")
            print(f"初始聊天天数: {initial_relationship.get('chat_days', 0)}")
            print(f"发送普通消息后聊天天数: {after_normal_message.get('chat_days', 0)}")
            print(f"发送新的一天消息后聊天天数: {after_new_day.get('chat_days', 0)}")
            
            if after_new_day.get('chat_days', 0) > initial_relationship.get('chat_days', 0):
                print("\n✅ 测试成功：聊天天数成功增加！")
            else:
                print("\n❌ 测试失败：聊天天数没有增加！") 