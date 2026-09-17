"""
依赖注入：数据库会话、用户认证
"""
from typing import Generator
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database.config import SessionLocal
from database.models import Organizer
from app.core.security import decode_access_token


class _HTTPBearer401(HTTPBearer):
    """HTTPBearer 定制版：无 token 时返回 401 而不是 403"""

    def __init__(self):
        super().__init__(auto_error=True)

    async def __call__(self, request: Request):
        credentials = await super().__call__(request)
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="未提供认证令牌",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return credentials


# HTTP Bearer Token 认证
security = _HTTPBearer401()


def get_db() -> Generator:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Organizer:
    """获取当前登录用户"""
    token = credentials.credentials
    
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(Organizer).filter(Organizer.id == int(user_id)).first()
    if user is None or user.status != 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已禁用",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user
