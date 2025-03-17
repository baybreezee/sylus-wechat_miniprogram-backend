import requests
import json
import time
from datetime import datetime
import os

# 设置基础URL
BASE_URL = "http://localhost:2100"  # 使用本地2100端口
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0X3VzZXJfaWQiLCJleHAiOjk5OTk5OTk5OTl9.mock_signature"  # 模拟token

def print_divider(title):
    """打印分隔线"""
    print("\n" + "="*50)
    print(f"  {title}")
    print("="*50)

def test_response(response, name):
    """测试响应并打印详细信息"""
    print(f"\n【{name}】状态码: {response.status_code}")
    
    try:
        result = response.json()
        print(f"响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return result
    except:
        print(f"响应内容: {response.text}")
        return None

# 1. 测试根路径接口
def test_root():
    print_divider("测试根路径接口")
    url = f"{BASE_URL}/"
    response = requests.get(url)
    test_response(response, "根路径")

# 2. 测试用户登录
def test_login():
    print_divider("测试用户登录")
    global token
    url = f"{BASE_URL}/api/users/login"  # 修改为users路由
    data = {"code": "0e1yGX0w3uSry434cC0w3NyK751yGX0i"}  # 使用新的微信临时登录凭证
    
    try:
        response = requests.post(url, json=data)
        result = test_response(response, "用户登录")
        
        if response.status_code == 200 and result and result.get("access_token"):
            token = result.get("access_token")
            print(f"✅ 登录成功，获取到token: {token[:10]}...")
            return True
        else:
            print("❌ 登录失败，将使用模拟token继续测试其他接口")
            return False
    except Exception as e:
        print(f"❌ 登录请求异常: {str(e)}")
        print("将使用模拟token继续测试其他接口")
        return False

# 3. 测试获取用户信息
def test_get_user_info():
    print_divider("测试获取用户信息")
    url = f"{BASE_URL}/api/users/me"  # 修改为正确的路由
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        test_response(response, "获取用户信息")
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")

# 4. 测试更新用户信息
def test_update_user_info():
    print_divider("测试更新用户信息")
    url = f"{BASE_URL}/api/users/me"  # 修改为正确的路由
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "nickname": f"测试用户_{int(time.time())}",
        "signature": "这是一条测试签名"
    }
    
    try:
        response = requests.put(url, headers=headers, json=data)
        test_response(response, "更新用户信息")
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")

# 5. 测试上传用户头像（模拟测试，无实际文件上传）
def test_upload_avatar():
    print_divider("测试上传用户头像 (模拟)")
    url = f"{BASE_URL}/api/users/avatar"  # 修改为正确的路由
    headers = {"Authorization": f"Bearer {token}"}
    
    print("注：此测试需要实际文件上传，此处只展示接口信息")
    print(f"请求URL: {url}")
    print(f"请求方法: POST")
    print(f"请求头: {headers}")
    print(f"请求体: multipart/form-data 包含 file 字段")
    print("预期响应: {'avatar_url': '/static/uploads/avatar_xxx.jpg'}")

# 6. 测试获取Sylus信息
def test_get_sylus_info():
    print_divider("测试获取Sylus信息")
    url = f"{BASE_URL}/api/sylus/info"  # 修改为正确的路由
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        test_response(response, "获取Sylus信息")
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")

# 7. 测试获取与Sylus的关系
def test_get_relationship():
    print_divider("测试获取与Sylus的关系")
    url = f"{BASE_URL}/api/relationship/status"  # 修改为正确的路由
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        test_response(response, "获取与Sylus的关系")
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")

# 8. 测试获取聊天记录
def test_get_chat_history():
    print_divider("测试获取聊天记录")
    url = f"{BASE_URL}/api/chat/history"  # 路由已正确
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        test_response(response, "获取聊天记录")
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")

# 9. 测试发送消息
def test_send_message():
    print_divider("测试发送消息")
    url = f"{BASE_URL}/api/chat/send"  # 修改为正确的路由
    headers = {"Authorization": f"Bearer {token}"}
    data = {"content": f"这是一条测试消息 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        result = test_response(response, "发送消息")
        
        if response.status_code in [200, 201] and result and result.get("id"):
            message_id = result.get("id")
            print(f"✅ 发送成功，消息ID: {message_id}")
            return message_id
        else:
            print("❌ 消息发送失败")
            return "mock_message_id"  # 返回模拟ID以便继续测试
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return "mock_message_id"  # 返回模拟ID以便继续测试

# 10. 测试获取AI回复
def test_get_ai_reply(message_id):
    print_divider("测试获取AI回复")
    if not message_id:
        message_id = "mock_message_id"
        print(f"使用模拟消息ID: {message_id}")
        
    url = f"{BASE_URL}/api/chat/ai_response"  # 修改为正确的路由
    headers = {"Authorization": f"Bearer {token}"}
    data = {"content": "请回复这条消息"}  # 修改为匹配新的ChatMessage模型
    
    try:
        response = requests.post(url, headers=headers, json=data)
        test_response(response, "获取AI回复")
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")

# 11. 测试获取朋友圈列表
def test_get_moments():
    print_divider("测试获取朋友圈列表")
    url = f"{BASE_URL}/api/moments"  # 修改为正确的路由
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        test_response(response, "获取朋友圈列表")
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")

# 12. 测试发布朋友圈
def test_create_moment():
    print_divider("测试发布朋友圈")
    url = f"{BASE_URL}/api/moments"  # 修改为正确的路由
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "content": f"这是一条测试朋友圈 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "images": []
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        result = test_response(response, "发布朋友圈")
        
        if response.status_code in [200, 201] and result and result.get("id"):
            moment_id = result.get("id")
            print(f"✅ 发布成功，朋友圈ID: {moment_id}")
            return moment_id
        else:
            print("❌ 朋友圈发布失败")
            return "mock_moment_id"  # 返回模拟ID以便继续测试
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return "mock_moment_id"  # 返回模拟ID以便继续测试

# 13. 测试上传朋友圈图片（模拟测试，无实际文件上传）
def test_upload_moment_image():
    print_divider("测试上传朋友圈图片 (模拟)")
    url = f"{BASE_URL}/api/moments/images"  # 修改为正确的路由
    headers = {"Authorization": f"Bearer {token}"}
    
    print("注：此测试需要实际文件上传，此处只展示接口信息")
    print(f"请求URL: {url}")
    print(f"请求方法: POST")
    print(f"请求头: {headers}")
    print(f"请求体: multipart/form-data 包含 file 字段")
    print("预期响应: {'image_url': '/static/uploads/moment_xxx.jpg'}")

# 14. 测试获取AI朋友圈回复
def test_get_moment_ai_response(moment_id):
    print_divider("测试获取AI朋友圈回复")
    if not moment_id:
        moment_id = "mock_moment_id"
        print(f"使用模拟朋友圈ID: {moment_id}")
        
    url = f"{BASE_URL}/api/moments/ai-response"  # 路由已正确
    headers = {"Authorization": f"Bearer {token}"}
    data = {"moment_id": moment_id}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        test_response(response, "获取AI朋友圈回复")
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")

# 15. 测试获取日记列表
def test_get_diaries():
    print_divider("测试获取日记列表")
    url = f"{BASE_URL}/api/diary/list"  # 修改为正确的路由
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        test_response(response, "获取日记列表")
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")

# 16. 测试发布日记
def test_create_diary():
    print_divider("测试发布日记")
    url = f"{BASE_URL}/api/diary"  # 修改为正确的路由
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "title": f"测试日记 - {datetime.now().strftime('%Y-%m-%d')}",
        "content": f"这是一篇测试日记 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "mood": "happy"  # 使用小写的枚举值
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        result = test_response(response, "发布日记")
        
        if response.status_code in [200, 201] and result and result.get("id"):
            diary_id = result.get("id")
            print(f"✅ 发布成功，日记ID: {diary_id}")
            return diary_id
        else:
            print("❌ 日记发布失败")
            return "mock_diary_id"  # 返回模拟ID以便继续测试
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return "mock_diary_id"  # 返回模拟ID以便继续测试

# 17. 测试获取AI日记回复
def test_get_diary_ai_response(diary_id):
    print_divider("测试获取AI日记回复")
    if not diary_id:
        diary_id = "mock_diary_id"
        print(f"使用模拟日记ID: {diary_id}")
        
    url = f"{BASE_URL}/api/diary/ai-response"  # 修改为正确的路由
    headers = {"Authorization": f"Bearer {token}"}
    data = {"diary_id": diary_id}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        test_response(response, "获取AI日记回复")
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")

# 18. 测试获取相册列表
def test_get_albums():
    print_divider("测试获取相册列表")
    url = f"{BASE_URL}/api/album/list"  # 修改为正确的路由
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        test_response(response, "获取相册列表")
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")

# 19. 测试上传相册照片（模拟测试，无实际文件上传）
def test_upload_album_photo():
    print_divider("测试上传相册照片 (模拟)")
    url = f"{BASE_URL}/api/album/upload-photo"  # 修改为正确的路由
    headers = {"Authorization": f"Bearer {token}"}
    
    print("注：此测试需要实际文件上传，此处只展示接口信息")
    print(f"请求URL: {url}")
    print(f"请求方法: POST")
    print(f"请求头: {headers}")
    print(f"请求体: multipart/form-data 包含 file、album_id、title 字段")
    print("预期响应: {'id': '...', 'album_id': '...', 'image_url': '/static/uploads/album_xxx.jpg', ...}")

# 14.1 测试朋友圈点赞
def test_like_moment(moment_id):
    print_divider("测试朋友圈点赞")
    if not moment_id or moment_id == "mock_moment_id":
        print("没有可用的朋友圈ID，跳过点赞测试")
        return
        
    url = f"{BASE_URL}/api/moments/{moment_id}/like"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(url, headers=headers)
        test_response(response, "朋友圈点赞")
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")

# 14.2 测试朋友圈评论
def test_comment_moment(moment_id):
    print_divider("测试朋友圈评论")
    if not moment_id or moment_id == "mock_moment_id":
        print("没有可用的朋友圈ID，跳过评论测试")
        return
        
    url = f"{BASE_URL}/api/moments/{moment_id}/comment"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"content": f"这是一条测试评论 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        test_response(response, "朋友圈评论")
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")

# 运行所有测试
def run_all_tests():
    print_divider("开始测试所有接口")
    print(f"API根地址: {BASE_URL}")
    
    # 1. 测试根路径
    test_root()
    
    # 2. 测试登录
    login_success = test_login()
    
    # 3-7. 用户和Sylus相关测试
    test_get_user_info()
    test_update_user_info()
    test_upload_avatar()
    test_get_sylus_info()
    test_get_relationship()
    
    # 8-10. 聊天相关测试
    test_get_chat_history()
    message_id = test_send_message()
    test_get_ai_reply(message_id)
    
    # 11-14. 朋友圈相关测试
    test_get_moments()
    moment_id = test_create_moment()
    test_upload_moment_image()
    # 新增的朋友圈点赞和评论测试
    test_like_moment(moment_id)
    test_comment_moment(moment_id)
    test_get_moment_ai_response(moment_id)
    
    # 15-17. 日记相关测试
    test_get_diaries()
    diary_id = test_create_diary()
    test_get_diary_ai_response(diary_id)
    
    # 18-19. 相册相关测试
    test_get_albums()
    test_upload_album_photo()
    
    print_divider("所有接口测试完成")
    if not login_success:
        print("\n⚠️ 注意：登录失败，所有需要认证的接口可能会返回401错误。")
        print("这是正常的，因为我们使用了模拟token，它不是服务器认可的有效token。")

# 执行全部测试
if __name__ == "__main__":
    run_all_tests() 