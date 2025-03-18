import json
import time
from datetime import datetime
import os
import aiohttp
import asyncio

# 设置基础URL
BASE_URL = "http://localhost:2100"  # 使用本地2100端口
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0X3VzZXJfaWQiLCJleHAiOjk5OTk5OTk5OTl9.mock_signature"  # 模拟token
headers = {"Authorization": f"Bearer {token}"}

def print_divider(title):
    """打印分隔线"""
    print("\n" + "="*50)
    print(f"  {title}")
    print("="*50)

async def test_response(response, name):
    """测试响应并打印详细信息"""
    print(f"\n【{name}】状态码: {response.status}")
    
    try:
        result = await response.json()
        print(f"响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return result
    except:
        text = await response.text()
        print(f"响应内容: {text}")
        return None

# 1. 测试根路径接口
async def test_root():
    print_divider("测试根路径接口")
    url = f"{BASE_URL}/"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                result = await test_response(response, "根路径")
                return response
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return None

# 2. 测试用户登录
async def test_login():
    print_divider("测试用户登录")
    global token
    url = f"{BASE_URL}/api/users/login"  # 修改为users路由
    data = {"code": "0e1yGX0w3uSry434cC0w3NyK751yGX0i"}  # 使用新的微信临时登录凭证
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                result = await test_response(response, "用户登录")
                
                if response.status == 200 and result and result.get("access_token"):
                    token = result.get("access_token")
                    print(f"✅ 登录成功，获取到token: {token[:10]}...")
                    return response
                else:
                    print("❌ 登录失败，将使用模拟token继续测试其他接口")
                    return None
    except Exception as e:
        print(f"❌ 登录请求异常: {str(e)}")
        print("将使用模拟token继续测试其他接口")
        return None

# 3. 测试获取用户信息
async def test_get_user_info():
    print_divider("测试获取用户信息")
    url = f"{BASE_URL}/api/users/me"  # 修改为正确的路由
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                result = await test_response(response, "获取用户信息")
                return response
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return None

# 4. 测试更新用户信息
async def test_update_user_info():
    print_divider("测试更新用户信息")
    url = f"{BASE_URL}/api/users/me"  # 修改为正确的路由
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "nickname": f"测试用户_{int(time.time())}",
        "signature": "这是一条测试签名"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.put(url, headers=headers, json=data) as response:
                result = await test_response(response, "更新用户信息")
                return response
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return None

# 5. 测试上传用户头像（模拟测试，无实际文件上传）
async def test_upload_avatar():
    print_divider("测试上传用户头像 (模拟)")
    url = f"{BASE_URL}/api/users/avatar"  # 修改为正确的路由
    headers = {"Authorization": f"Bearer {token}"}
    
    print("注：此测试需要实际文件上传，此处只展示接口信息")
    print(f"请求URL: {url}")
    print(f"请求方法: POST")
    print(f"请求头: {headers}")
    print(f"请求体: multipart/form-data 包含 file 字段")
    print("预期响应: {'avatar_url': '/static/uploads/avatar_xxx.jpg'}")
    return None

# 6. 测试获取Sylus信息
async def test_get_sylus_info():
    print_divider("测试获取Sylus信息")
    url = f"{BASE_URL}/api/sylus/info"  # 修改为正确的路由
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                result = await test_response(response, "获取Sylus信息")
                return response
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return None

# 7. 测试获取与Sylus的关系
async def test_get_relationship():
    print_divider("测试获取与Sylus的关系")
    url = f"{BASE_URL}/api/relationship/status"  # 修改为正确的路由
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                result = await test_response(response, "获取与Sylus的关系")
                return response
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return None

# 8. 测试获取聊天记录
async def test_get_chat_history():
    print_divider("测试获取聊天记录")
    url = f"{BASE_URL}/api/chat/history"  # 路由已正确
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                result = await test_response(response, "获取聊天记录")
                return response
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return None

# 9. 测试发送消息
async def test_send_message():
    print_divider("测试发送消息")
    url = f"{BASE_URL}/api/chat/send"  # 修改为正确的路由
    headers = {"Authorization": f"Bearer {token}"}
    data = {"content": f"这是一条测试消息 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                result = await test_response(response, "发送消息")
                
                if response.status in [200, 201] and result and result.get("id"):
                    message_id = result.get("id")
                    print(f"✅ 发送成功，消息ID: {message_id}")
                    return response
                else:
                    print("❌ 消息发送失败")
                    return None
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return None

# 10. 测试获取AI回复
async def test_get_ai_reply(message_id):
    print_divider("测试获取AI回复")
    if not message_id:
        message_id = "mock_message_id"
        print(f"使用模拟消息ID: {message_id}")
        
    url = f"{BASE_URL}/api/chat/ai_response"  # 修改为正确的路由
    headers = {"Authorization": f"Bearer {token}"}
    data = {"content": "请回复这条消息"}  # 修改为匹配新的ChatMessage模型
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                result = await test_response(response, "获取AI回复")
                return response
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return None

# 11. 测试获取朋友圈列表
async def test_get_moments():
    print_divider("测试获取朋友圈列表")
    url = f"{BASE_URL}/api/moments"  # 修改为正确的路由
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                result = await test_response(response, "获取朋友圈列表")
                return response
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return None

# 12. 测试发布朋友圈
async def test_create_moment():
    print_divider("测试发布朋友圈")
    url = f"{BASE_URL}/api/moments"  # 修改为正确的路由
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "content": f"这是一条测试朋友圈 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "images": []
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                result = await test_response(response, "发布朋友圈")
                
                if response.status in [200, 201] and result and result.get("id"):
                    moment_id = result.get("id")
                    print(f"✅ 发布成功，朋友圈ID: {moment_id}")
                    return response
                else:
                    print("❌ 朋友圈发布失败")
                    return None
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return None

# 13. 测试上传朋友圈图片（模拟测试，无实际文件上传）
async def test_upload_moment_image():
    print_divider("测试上传朋友圈图片 (模拟)")
    url = f"{BASE_URL}/api/moments/images"  # 修改为正确的路由
    headers = {"Authorization": f"Bearer {token}"}
    
    print("注：此测试需要实际文件上传，此处只展示接口信息")
    print(f"请求URL: {url}")
    print(f"请求方法: POST")
    print(f"请求头: {headers}")
    print(f"请求体: multipart/form-data 包含 file 字段")
    print("预期响应: {'image_url': '/static/uploads/moment_xxx.jpg'}")
    return None

# 14. 测试获取AI朋友圈回复
async def test_get_moment_ai_response(moment_id):
    print_divider("测试获取AI朋友圈回复")
    if not moment_id:
        moment_id = "mock_moment_id"
        print(f"使用模拟朋友圈ID: {moment_id}")
        
    url = f"{BASE_URL}/api/moments/{moment_id}/ai-response"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"moment_id": moment_id}  # 添加moment_id到请求体
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                result = await test_response(response, "获取AI朋友圈回复")
                return response
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return None

# 15. 测试获取日记列表
async def test_get_diaries():
    print_divider("测试获取日记列表")
    url = f"{BASE_URL}/api/diary/list"  # 修改为正确的路由
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                result = await test_response(response, "获取日记列表")
                return response
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return None

# 16. 测试发布日记
async def test_create_diary():
    print_divider("测试发布日记")
    url = f"{BASE_URL}/api/diary"  # 修改为正确的路由
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "title": f"测试日记 - {datetime.now().strftime('%Y-%m-%d')}",
        "content": f"这是一篇测试日记 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "mood": "happy"  # 使用小写的枚举值
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                result = await test_response(response, "发布日记")
                
                if response.status in [200, 201] and result and result.get("id"):
                    diary_id = result.get("id")
                    print(f"✅ 发布成功，日记ID: {diary_id}")
                    return response
                else:
                    print("❌ 日记发布失败")
                    return None
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return None

# 17. 测试获取AI日记回复
async def test_get_diary_ai_response(diary_id):
    print_divider("测试获取AI日记回复")
    if not diary_id:
        diary_id = "mock_diary_id"
        print(f"使用模拟日记ID: {diary_id}")
        
    url = f"{BASE_URL}/api/diary/ai-response"  # 修改为正确的路由
    headers = {"Authorization": f"Bearer {token}"}
    data = {"diary_id": diary_id}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                result = await test_response(response, "获取AI日记回复")
                return response
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return None

# 18. 测试获取相册列表
async def test_get_albums():
    print_divider("测试获取相册列表")
    url = f"{BASE_URL}/api/album/list"  # 修改为正确的路由
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                result = await test_response(response, "获取相册列表")
                return response
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return None

# 14.1 测试朋友圈点赞/取消点赞
async def test_like_moment(moment_id):
    print_divider("测试朋友圈点赞/取消点赞")
    if not moment_id or moment_id == "mock_moment_id":
        print("没有可用的朋友圈ID，跳过点赞测试")
        return None
        
    url = f"{BASE_URL}/api/moments/{moment_id}/like"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers) as response:
                result = await test_response(response, "朋友圈点赞")
                return response
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return None

# 14.2 测试朋友圈评论
async def test_comment_moment(moment_id):
    print_divider("测试朋友圈评论")
    if not moment_id or moment_id == "mock_moment_id":
        print("没有可用的朋友圈ID，跳过评论测试")
        return None
        
    url = f"{BASE_URL}/api/moments/{moment_id}/comment"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"content": f"这是一条测试评论 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                result = await test_response(response, "朋友圈评论")
                return response
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return None

# 14.4 测试删除朋友圈评论
async def test_delete_comment(moment_id, comment_id):
    print_divider("测试删除朋友圈评论")
    if not moment_id or moment_id == "mock_moment_id" or not comment_id:
        print("没有可用的朋友圈ID或评论ID，跳过删除评论测试")
        return None
        
    url = f"{BASE_URL}/api/moments/{moment_id}/comments/{comment_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=headers) as response:
                result = await test_response(response, "删除朋友圈评论")
                return response
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return None

# 14.5 测试删除朋友圈
async def test_delete_moment(moment_id):
    print_divider("测试删除朋友圈")
    if not moment_id or moment_id == "mock_moment_id":
        print("没有可用的朋友圈ID，跳过删除朋友圈测试")
        return None
        
    url = f"{BASE_URL}/api/moments/{moment_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=headers) as response:
                result = await test_response(response, "删除朋友圈")
                return response
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return None

# 运行所有测试
async def run_all_tests():
    """运行所有测试"""
    print("\n=== 开始运行所有测试 ===")
    
    # 登录测试
    print("\n--- 登录测试 ---")
    login_response = await test_login()
    if login_response and login_response.status == 200:
        print("✅ 登录成功")
        result = await login_response.json()
        token = result.get("access_token")
        if token:
            headers["Authorization"] = f"Bearer {token}"
    else:
        print("❌ 登录失败")
        return

    # 获取用户信息测试
    print("\n--- 获取用户信息测试 ---")
    user_info_response = await test_get_user_info()
    if user_info_response and user_info_response.status == 200:
        print("✅ 获取用户信息成功")
    else:
        print("❌ 获取用户信息失败")

    # 更新用户信息测试
    print("\n--- 更新用户信息测试 ---")
    update_response = await test_update_user_info()
    if update_response and update_response.status == 200:
        print("✅ 更新用户信息成功")
    else:
        print("❌ 更新用户信息失败")

    # 获取Sylus信息测试
    print("\n--- 获取Sylus信息测试 ---")
    sylus_response = await test_get_sylus_info()
    if sylus_response and sylus_response.status == 200:
        print("✅ 获取Sylus信息成功")
    else:
        print("❌ 获取Sylus信息失败")

    # 获取与Sylus的关系测试
    print("\n--- 获取与Sylus的关系测试 ---")
    relationship_response = await test_get_relationship()
    if relationship_response and relationship_response.status == 200:
        print("✅ 获取与Sylus的关系成功")
    else:
        print("❌ 获取与Sylus的关系失败")

    # 发送消息测试
    print("\n--- 发送消息测试 ---")
    message_response = await test_send_message()
    if message_response and message_response.status == 200:
        print("✅ 发送消息成功")
    else:
        print("❌ 发送消息失败")

    # 获取聊天历史测试
    print("\n--- 获取聊天历史测试 ---")
    history_response = await test_get_chat_history()
    if history_response and history_response.status == 200:
        print("✅ 获取聊天历史成功")
    else:
        print("❌ 获取聊天历史失败")

    # 发布朋友圈测试
    print("\n--- 发布朋友圈测试 ---")
    moment_response = await test_create_moment()
    if moment_response and moment_response.status == 200:
        print("✅ 发布朋友圈成功")
        result = await moment_response.json()
        moment_id = result.get("id")
    else:
        print("❌ 发布朋友圈失败")
        moment_id = None

    # 获取朋友圈列表测试
    print("\n--- 获取朋友圈列表测试 ---")
    moments_response = await test_get_moments()
    if moments_response and moments_response.status == 200:
        print("✅ 获取朋友圈列表成功")
    else:
        print("❌ 获取朋友圈列表失败")

    # 点赞测试
    print("\n--- 点赞测试 ---")
    if moment_id:
        like_response = await test_like_moment(moment_id)
        if like_response and like_response.status == 200:
            print("✅ 点赞成功")
        else:
            print("❌ 点赞失败")

        # 取消点赞测试
        unlike_response = await test_like_moment(moment_id)
        if unlike_response and unlike_response.status == 200:
            print("✅ 取消点赞成功")
        else:
            print("❌ 取消点赞失败")

    # 评论测试
    print("\n--- 评论测试 ---")
    if moment_id:
        comment_response = await test_comment_moment(moment_id)
        if comment_response and comment_response.status == 200:
            print("✅ 评论成功")
            result = await comment_response.json()
            comment_id = result.get("id")
        else:
            print("❌ 评论失败")
            comment_id = None

        # 删除评论测试
        if comment_id:
            delete_comment_response = await test_delete_comment(moment_id, comment_id)
            if delete_comment_response and delete_comment_response.status == 200:
                print("✅ 删除评论成功")
            else:
                print("❌ 删除评论失败")

    # 删除朋友圈测试
    print("\n--- 删除朋友圈测试 ---")
    if moment_id:
        delete_response = await test_delete_moment(moment_id)
        if delete_response and delete_response.status == 200:
            print("✅ 删除朋友圈成功")
        else:
            print("❌ 删除朋友圈失败")

    # AI回复测试
    print("\n--- AI回复测试 ---")
    if moment_id:
        ai_response = await test_get_moment_ai_response(moment_id)
        if ai_response and ai_response.status == 200:
            print("✅ AI回复成功")
        else:
            print("❌ AI回复失败")

    # 发布日记测试
    print("\n--- 发布日记测试 ---")
    diary_response = await test_create_diary()
    if diary_response and diary_response.status == 200:
        print("✅ 发布日记成功")
        result = await diary_response.json()
        diary_id = result.get("id")
    else:
        print("❌ 发布日记失败")
        diary_id = None

    # 获取日记列表测试
    print("\n--- 获取日记列表测试 ---")
    diaries_response = await test_get_diaries()
    if diaries_response and diaries_response.status == 200:
        print("✅ 获取日记列表成功")
    else:
        print("❌ 获取日记列表失败")

    # AI日记回复测试
    print("\n--- AI日记回复测试 ---")
    if diary_id:
        diary_ai_response = await test_get_diary_ai_response(diary_id)
        if diary_ai_response and diary_ai_response.status == 200:
            print("✅ AI日记回复成功")
        else:
            print("❌ AI日记回复失败")

    # 获取相册列表测试
    print("\n--- 获取相册列表测试 ---")
    albums_response = await test_get_albums()
    if albums_response and albums_response.status == 200:
        print("✅ 获取相册列表成功")
    else:
        print("❌ 获取相册列表失败")

    print("\n=== 测试完成 ===")

# 执行全部测试
if __name__ == "__main__":
    asyncio.run(run_all_tests()) 