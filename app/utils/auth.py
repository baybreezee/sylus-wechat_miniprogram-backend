from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from bson import ObjectId

from app.config.settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.models.user import UserInDB
from app.config.database import users_collection

# OAuth2 认证方案
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

# 密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token模型
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    openid: Optional[str] = None

# 验证密码
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# 获取密码哈希
def get_password_hash(password):
    return pwd_context.hash(password)

# 获取用户
def get_user(openid: str):
    user_dict = users_collection.find_one({"openid": openid})
    if user_dict:
        # 将ObjectId转换为字符串
        if "_id" in user_dict and isinstance(user_dict["_id"], ObjectId):
            user_dict["_id"] = str(user_dict["_id"])
        return UserInDB(**user_dict)
    return None

# 验证用户
def authenticate_user(openid: str, password: str):
    user = get_user(openid)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

# 创建访问令牌
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 获取当前用户
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        openid: str = payload.get("sub")
        if openid is None:
            raise credentials_exception
        token_data = TokenData(openid=openid)
    except JWTError:
        raise credentials_exception
    
    user = get_user(openid=token_data.openid)
    if user is None:
        raise credentials_exception
    return user

# 获取当前活跃用户
async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="用户已被禁用")
    return current_user 