"""
认证 API：注册、登录、获取用户信息
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from database.config import get_db
from database.models import Organizer
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.dependencies import get_current_user
from app.core.config import settings


router = APIRouter()


# ========== Pydantic 模型 ==========

class RegisterRequest(BaseModel):
    """注册请求"""
    username: str
    password: str
    organizer_name: str
    contact_person: str
    phone: str
    email: EmailStr
    address: str = None


class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str
    token_type: str = "bearer"
    user_info: dict


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    organizer_name: str
    contact_person: str
    phone: str
    email: str
    address: str = None
    
    class Config:
        from_attributes = True


# ========== API 接口 ==========

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """主办方注册"""
    
    # 检查用户名是否已存在
    existing = db.query(Organizer).filter(
        (Organizer.username == request.username) | 
        (Organizer.email == request.email)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名或邮箱已被注册"
        )
    
    # 创建新用户
    organizer = Organizer(
        username=request.username,
        password_hash=get_password_hash(request.password),
        organizer_name=request.organizer_name,
        contact_person=request.contact_person,
        phone=request.phone,
        email=request.email,
        address=request.address,
        status=1
    )
    
    db.add(organizer)
    db.commit()
    db.refresh(organizer)
    
    return {
        "message": "注册成功",
        "user_id": organizer.id
    }


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    
    # 查找用户
    organizer = db.query(Organizer).filter(
        Organizer.username == request.username
    ).first()
    
    if not organizer or not verify_password(request.password, organizer.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if organizer.status != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用"
        )
    
    # 生成 Token
    access_token = create_access_token(
        data={"sub": str(organizer.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    # 更新最后登录时间
    from datetime import datetime
    organizer.last_login_at = datetime.now()
    db.commit()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_info": {
            "id": organizer.id,
            "username": organizer.username,
            "organizer_name": organizer.organizer_name
        }
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: Organizer = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user
