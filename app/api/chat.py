"""
AI 对话 API
支持 session 上下文记忆，连续对话沿用已锁定的活动。
"""
import uuid
import time
from collections import defaultdict
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from database.config import get_db
from database.models import ChatLog, Activity
from app.services.ai_service import generate_ai_response


router = APIRouter()

# ========== 简单频率限制（内存版） ==========
# ip -> [最近请求时间戳]
_RATE_LIMIT_WINDOW = 60        # 时间窗口：60 秒
_RATE_LIMIT_MAX = 30           # 每窗口最多 30 次请求
_rate_limit_store = defaultdict(list)


def _check_rate_limit(client_ip: str):
    """检查并记录频率限制，超限抛出 429"""
    now = time.time()
    window_start = now - _RATE_LIMIT_WINDOW
    _rate_limit_store[client_ip] = [
        ts for ts in _rate_limit_store[client_ip] if ts > window_start
    ]
    if len(_rate_limit_store[client_ip]) >= _RATE_LIMIT_MAX:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="请求过于频繁，请稍后再试",
        )
    _rate_limit_store[client_ip].append(now)


class ChatRequest(BaseModel):
    message: str
    activity_id: Optional[int] = None
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    activity_name: Optional[str] = None


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: list
    created_at: datetime


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, http_request: Request, db: Session = Depends(get_db)):
    """与 AI 助手对话（支持上下文记忆）"""
    
    # 频率限制
    client_ip = http_request.client.host if http_request.client else "unknown"
    _check_rate_limit(client_ip)

    session_id = request.session_id or str(uuid.uuid4())

    try:
        ai_response = await generate_ai_response(
            message=request.message,
            db=db,
            session_id=session_id,
            activity_id=request.activity_id,
        )
    except Exception as e:
        ai_response = "抱歉，我暂时无法回答您的问题，请稍后重试。"

    # 查找关联的活动名称
    activity_name = None
    if request.activity_id:
        act = db.query(Activity).filter(Activity.id == request.activity_id).first()
        if act:
            activity_name = act.activity_name

    # 保存对话记录
    try:
        chat_log = ChatLog(
            session_id=session_id,
            activity_id=request.activity_id,
            user_message=request.message,
            assistant_response=ai_response,
        )
        db.add(chat_log)
        db.commit()
    except Exception:
        db.rollback()

    return ChatResponse(
        response=ai_response,
        session_id=session_id,
        activity_name=activity_name,
    )


@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
def get_chat_history(session_id: str, db: Session = Depends(get_db)):
    """获取会话历史记录"""

    logs = db.query(ChatLog).filter(
        ChatLog.session_id == session_id
    ).order_by(ChatLog.created_at.asc()).limit(50).all()

    if not logs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )

    messages = []
    for log in logs:
        messages.extend([
            {"type": "user", "content": log.user_message, "created_at": log.created_at},
            {"type": "assistant", "content": log.assistant_response, "created_at": log.created_at},
        ])

    return ChatHistoryResponse(
        session_id=session_id,
        messages=messages,
        created_at=logs[0].created_at,
    )