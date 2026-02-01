"""
英语学习辅助应用 - 用户认证模块

提供用户注册、登录、JWT Token生成和验证
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from supabase import create_client, Client

from config import settings
from database import User

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT配置
SECRET_KEY = settings.app.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天

# Supabase客户端
supabase: Client = create_client(
    settings.supabase.url,
    settings.supabase.service_key
)

# HTTP Bearer Token安全依赖
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建JWT访问令牌"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """解码JWT令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无法验证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """获取当前登录用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # 从Supabase获取用户
    try:
        response = supabase.table("users").select("*").eq("id", user_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise credentials_exception
        
        user_data = response.data[0]
        
        # 检查用户是否激活
        if not user_data.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="用户已被禁用"
            )
        
        return User(**user_data)
        
    except Exception as e:
        raise credentials_exception


async def get_current_user_from_email(email: str) -> Optional[User]:
    """根据邮箱获取用户"""
    try:
        response = supabase.table("users").select("*").eq("email", email).execute()
        
        if response.data and len(response.data) > 0:
            return User(**response.data[0])
        return None
        
    except Exception:
        return None


def create_user(email: str, password: str, user_type: str, name: str) -> User:
    """创建新用户"""
    # 检查邮箱是否已存在
    existing = supabase.table("users").select("id").eq("email", email).execute()
    if existing.data and len(existing.data) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册"
        )
    
    # 创建用户
    user_data = {
        "email": email,
        "password_hash": get_password_hash(password),
        "user_type": user_type,
        "name": name,
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    response = supabase.table("users").insert(user_data).execute()
    
    if not response.data or len(response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="用户创建失败"
        )
    
    return User(**response.data[0])


def authenticate_user(email: str, password: str) -> Optional[User]:
    """验证用户登录"""
    user = get_current_user_from_email(email)
    
    if not user:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    return user


def update_user_login_time(user_id: str):
    """更新用户最后登录时间"""
    supabase.table("users").update({
        "last_login_at": datetime.utcnow().isoformat()
    }).eq("id", user_id).execute()
