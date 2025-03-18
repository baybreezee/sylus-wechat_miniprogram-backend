import os
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, Depends, UploadFile, File, Query
from app.config.database import moments_collection, sylus_collection
from app.models.user import UserInDB
from app.models.moments import CreateMoment, CreateComment, MomentAIResponseRequest
from app.utils.auth import get_current_active_user
from app.services.ai_service import get_moments_response
from app.config.settings import UPLOAD_FOLDER
from bson import ObjectId
import bson

# 获取朋友圈列表
async def get_moments(
    limit: int = Query(10, ge=1, le=100),
    before_timestamp: Optional[datetime] = None,
    current_user: UserInDB = Depends(get_current_active_user)
):
    try:
        # 构建查询条件
        query = {}
        
        if before_timestamp:
            query["timestamp"] = {"$lt": before_timestamp}
        
        # 获取朋友圈消息，按时间倒序排列
        moments = list(moments_collection.find(query).sort("timestamp", -1).limit(limit))
        
        # 转换为响应格式
        result = []
        for moment in moments:
            result.append({
                "id": str(moment["_id"]),
                "user_id": moment["user_id"],
                "author_name": moment["author_name"],
                "author_avatar": moment.get("author_avatar"),
                "content": moment["content"],
                "images": moment.get("images", []),
                "location": moment.get("location"),
                "likes": moment.get("likes", []),
                "comments": moment.get("comments", []),
                "timestamp": moment["timestamp"]
            })
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取朋友圈列表失败: {str(e)}")

# 发布朋友圈
async def create_moment(
    moment: CreateMoment,
    current_user: UserInDB = Depends(get_current_active_user)
):
    try:
        # 创建朋友圈对象
        now = datetime.utcnow()
        new_moment = {
            "user_id": str(current_user.id) if current_user.id else current_user.openid,
            "author_name": current_user.nickname or "用户",
            "author_avatar": current_user.avatar,
            "content": moment.content,
            "images": moment.images,
            "location": moment.location,
            "likes": [],
            "comments": [],
            "timestamp": now
        }
        
        # 存储朋友圈
        result = moments_collection.insert_one(new_moment)
        moment_id = result.inserted_id
        
        # 返回已创建的朋友圈
        return {
            "id": str(moment_id),
            "user_id": new_moment["user_id"],
            "author_name": new_moment["author_name"],
            "author_avatar": new_moment["author_avatar"],
            "content": new_moment["content"],
            "images": new_moment["images"],
            "location": new_moment["location"],
            "likes": new_moment["likes"],
            "comments": new_moment["comments"],
            "timestamp": new_moment["timestamp"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发布朋友圈失败: {str(e)}")

# 上传朋友圈图片
async def upload_moment_image(
    file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_active_user)
):
    try:
        # 验证文件类型
        allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="不支持的文件类型，仅支持JPEG、PNG、GIF和WEBP格式")
        
        # 创建用户上传目录
        moments_dir = os.path.join(UPLOAD_FOLDER, "moments", str(current_user.id) if current_user.id else current_user.openid)
        os.makedirs(moments_dir, exist_ok=True)
        
        # 生成唯一文件名
        file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(moments_dir, unique_filename)
        
        # 保存文件
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # 返回图片URL
        image_url = f"/static/uploads/moments/{str(current_user.id) if current_user.id else current_user.openid}/{unique_filename}"
        return {"image_url": image_url}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"上传图片失败: {str(e)}")

# 点赞/取消点赞朋友圈
async def like_moment(
    moment_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    try:
        # 查找朋友圈
        moment = moments_collection.find_one({"_id": ObjectId(moment_id)})
        
        if not moment:
            raise HTTPException(status_code=404, detail="朋友圈不存在")
        
        # 用户ID
        user_id = str(current_user.id) if current_user.id else current_user.openid
        likes = moment.get("likes", [])
        
        # 检查是否已点赞
        has_liked = False
        for like in likes:
            if like.get("user_id") == user_id:
                has_liked = True
                break
        
        if has_liked:
            # 如果已点赞，则取消点赞
            result = moments_collection.update_one(
                {"_id": ObjectId(moment_id)},
                {"$pull": {"likes": {"user_id": user_id}}}
            )
            
            if result.modified_count == 0:
                raise HTTPException(status_code=500, detail="取消点赞失败")
            
            return {"message": "取消点赞成功", "action": "unlike"}
        else:
            # 如果未点赞，则添加点赞
            like_data = {
                "user_id": user_id,
                "name": current_user.nickname or "用户",
                "avatar": current_user.avatar,
                "is_sylus": False,
                "timestamp": datetime.utcnow()
            }
            
            result = moments_collection.update_one(
                {"_id": ObjectId(moment_id)},
                {"$push": {"likes": like_data}}
            )
            
            if result.modified_count == 0:
                raise HTTPException(status_code=500, detail="点赞失败")
            
            return {"message": "点赞成功", "action": "like"}
            
    except bson.errors.InvalidId:
        raise HTTPException(status_code=400, detail="无效的朋友圈ID格式")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")

# 评论朋友圈
async def comment_moment(
    moment_id: str,
    comment: CreateComment,
    current_user: UserInDB = Depends(get_current_active_user)
):
    try:
        # 查找朋友圈
        moment = moments_collection.find_one({"_id": ObjectId(moment_id)})
        
        if not moment:
            raise HTTPException(status_code=404, detail="朋友圈不存在")
        
        # 创建评论
        comment_id = str(uuid.uuid4())
        comment_data = {
            "id": comment_id,
            "user_id": str(current_user.id) if current_user.id else current_user.openid,
            "author_name": current_user.nickname or "用户",
            "author_avatar": current_user.avatar,
            "is_sylus": False,
            "content": comment.content,
            "timestamp": datetime.utcnow()
        }
        
        # 更新数据库
        result = moments_collection.update_one(
            {"_id": ObjectId(moment_id)},
            {"$push": {"comments": comment_data}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="评论失败")
        
        return comment_data
    except bson.errors.InvalidId:
        raise HTTPException(status_code=400, detail="无效的朋友圈ID格式")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"评论失败: {str(e)}")

# 获取AI回应
async def get_ai_moment_response(
    request: MomentAIResponseRequest,
    current_user: UserInDB = Depends(get_current_active_user)
):
    try:
        # 查找朋友圈
        moment = moments_collection.find_one({"_id": ObjectId(request.moment_id)})
        
        if not moment:
            raise HTTPException(status_code=404, detail="朋友圈不存在")
        
        # 获取Sylus信息
        sylus = sylus_collection.find_one()
        if not sylus:
            raise HTTPException(status_code=404, detail="Sylus信息未找到")
        
        # 从AI服务获取回复
        sylus_personality = sylus.get("personality", "温柔体贴，善解人意")
        ai_response = await get_moments_response(moment["content"], sylus_personality)
        
        # 判断是点赞还是评论
        response_type = getattr(ai_response, 'response_type', None)
        if response_type == "like":
            # 检查是否已点赞
            likes = moment.get("likes", [])
            for like in likes:
                if like.get("is_sylus", False):
                    return {"message": "Sylus已经点过赞了", "action": "none"}
            
            # 添加点赞
            like_data = {
                "user_id": None,
                "name": sylus["name"],
                "avatar": sylus["avatar"],
                "is_sylus": True,
                "timestamp": datetime.utcnow()
            }
            
            # 更新数据库
            result = moments_collection.update_one(
                {"_id": ObjectId(request.moment_id)},
                {"$push": {"likes": like_data}}
            )
            
            if result.modified_count == 0:
                raise HTTPException(status_code=500, detail="点赞失败")
            
            return {"message": "Sylus点赞成功", "action": "like"}
        else:
            # 添加评论
            comment_data = {
                "id": str(ObjectId()),
                "user_id": None,
                "name": sylus["name"],
                "avatar": sylus["avatar"],
                "content": ai_response.response,
                "is_sylus": True,
                "timestamp": datetime.utcnow()
            }
            
            # 更新数据库
            result = moments_collection.update_one(
                {"_id": ObjectId(request.moment_id)},
                {"$push": {"comments": comment_data}}
            )
            
            if result.modified_count == 0:
                raise HTTPException(status_code=500, detail="评论失败")
            
            return {"message": "Sylus评论成功", "action": "comment", "content": comment_data["content"]}
    except bson.errors.InvalidId:
        raise HTTPException(status_code=400, detail="无效的朋友圈ID格式")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取AI朋友圈回复出错: {str(e)}")

# 删除朋友圈
async def delete_moment(
    moment_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    try:
        # 查找朋友圈
        moment = moments_collection.find_one({"_id": ObjectId(moment_id)})
        
        if not moment:
            raise HTTPException(status_code=404, detail="朋友圈不存在")
        
        # 检查是否是发布者
        user_id = str(current_user.id) if current_user.id else current_user.openid
        if moment["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="只有发布者可以删除朋友圈")
        
        # 删除朋友圈
        result = moments_collection.delete_one({"_id": ObjectId(moment_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=500, detail="删除朋友圈失败")
        
        return {"message": "删除朋友圈成功"}
        
    except bson.errors.InvalidId:
        raise HTTPException(status_code=400, detail="无效的朋友圈ID格式")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"删除朋友圈失败: {str(e)}")

# 删除评论
async def delete_comment(
    moment_id: str,
    comment_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    try:
        # 查找朋友圈
        moment = moments_collection.find_one({"_id": ObjectId(moment_id)})
        
        if not moment:
            raise HTTPException(status_code=404, detail="朋友圈不存在")
        
        # 查找评论
        comments = moment.get("comments", [])
        comment_to_delete = None
        for comment in comments:
            if comment.get("id") == comment_id:
                comment_to_delete = comment
                break
        
        if not comment_to_delete:
            raise HTTPException(status_code=404, detail="评论不存在")
        
        # 检查是否是评论发布者
        user_id = str(current_user.id) if current_user.id else current_user.openid
        if comment_to_delete.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="只有评论发布者可以删除评论")
        
        # 删除评论
        result = moments_collection.update_one(
            {"_id": ObjectId(moment_id)},
            {"$pull": {"comments": {"id": comment_id}}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="删除评论失败")
        
        return {"message": "删除评论成功"}
        
    except bson.errors.InvalidId:
        raise HTTPException(status_code=400, detail="无效的朋友圈ID格式")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"删除评论失败: {str(e)}") 