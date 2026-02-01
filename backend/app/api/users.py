"""
英语学习辅助应用 - 用户认证API路由

提供用户注册、登录等接口
"""

from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr

from auth import (
    create_user, 
    authenticate_user, 
    create_access_token, 
    update_user_login_time,
    get_current_user
)
from database import User

router = APIRouter()


# 请求/响应模型
class UserRegisterRequest(BaseModel):
    """用户注册请求"""
    email: EmailStr
    password: str
    user_type: str  # parent, student
    name: str


class UserLoginRequest(BaseModel):
    """用户登录请求"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """用户响应"""
    id: str
    email: str
    user_type: str
    name: str
    avatar_url: str | None = None
    created_at: str | None = None


class TokenResponse(BaseModel):
    """令牌响应"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegisterRequest):
    """用户注册"""
    # 验证用户类型
    if user_data.user_type not in ["parent", "student"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户类型必须为 'parent' 或 'student'"
        )
    
    # 验证密码强度
    if len(user_data.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码长度至少6位"
        )
    
    try:
        # 创建用户
        user = create_user(
            email=user_data.email,
            password=user_data.password,
            user_type=user_data.user_type,
            name=user_data.name
        )
        
        # 生成Token
        access_token_expires = timedelta(minutes=60 * 24 * 7)  # 7天
        access_token = create_access_token(
            data={"sub": user.id},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "user_type": user.user_type,
                "name": user.name,
                "avatar_url": user.avatar_url,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLoginRequest):
    """用户登录"""
    user = authenticate_user(credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查用户是否激活
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    # 更新最后登录时间
    update_user_login_time(user.id)
    
    # 生成Token
    access_token_expires = timedelta(minutes=60 * 24 * 7)  # 7天
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "user_type": user.user_type,
            "name": user.name,
            "avatar_url": user.avatar_url,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "user_type": current_user.user_type,
        "name": current_user.name,
        "avatar_url": current_user.avatar_url,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    }
