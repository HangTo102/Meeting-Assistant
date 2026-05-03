"""
活动管理 API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from database.config import get_db
from database.models import Activity, Organizer
from app.core.dependencies import get_current_user


router = APIRouter()


# ========== Pydantic 模型 ==========

class ActivityCreate(BaseModel):
    """创建活动请求"""
    activity_name: str
    start_time: datetime
    end_time: datetime
    address: str
    description: Optional[str] = None
    requires_ticket: bool = False
    ticket_url: Optional[str] = None
    ticket_price: Optional[str] = None
    ticket_deadline: Optional[datetime] = None
    status: int = 1


class ActivityUpdate(BaseModel):
    """更新活动请求"""
    activity_name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    address: Optional[str] = None
    description: Optional[str] = None
    requires_ticket: Optional[bool] = None
    ticket_url: Optional[str] = None
    ticket_price: Optional[str] = None
    ticket_deadline: Optional[datetime] = None
    status: Optional[int] = None


class ActivityResponse(BaseModel):
    """活动响应"""
    id: int
    organizer_id: int
    activity_name: str
    start_time: datetime
    end_time: datetime
    address: str
    description: Optional[str] = None
    requires_ticket: bool
    ticket_url: Optional[str] = None
    ticket_price: Optional[str] = None
    ticket_deadline: Optional[datetime] = None
    status: int
    view_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ========== API 接口 ==========

@router.post("/", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
def create_activity(
    request: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: Organizer = Depends(get_current_user)
):
    """创建活动"""
    
    activity = Activity(
        organizer_id=current_user.id,
        **request.model_dump()
    )
    
    db.add(activity)
    db.commit()
    db.refresh(activity)
    
    return activity


@router.get("/", response_model=List[ActivityResponse])
def get_activities(
    status_filter: Optional[int] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取活动列表"""
    
    query = db.query(Activity).filter(Activity.status != 3)  # 排除已取消
    
    if status_filter is not None:
        query = query.filter(Activity.status == status_filter)
    
    # 分页
    offset = (page - 1) * page_size
    activities = query.order_by(Activity.start_time.desc()).offset(offset).limit(page_size).all()
    
    return activities


@router.get("/{activity_id}", response_model=ActivityResponse)
def get_activity(activity_id: int, db: Session = Depends(get_db)):
    """获取活动详情"""
    
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活动不存在"
        )
    
    # 增加浏览次数
    activity.view_count += 1
    db.commit()
    
    return activity


@router.put("/{activity_id}", response_model=ActivityResponse)
def update_activity(
    activity_id: int,
    request: ActivityUpdate,
    db: Session = Depends(get_db),
    current_user: Organizer = Depends(get_current_user)
):
    """更新活动"""
    
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活动不存在"
        )
    
    # 检查权限
    if activity.organizer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此活动"
        )
    
    # 更新字段
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(activity, field, value)
    
    db.commit()
    db.refresh(activity)
    
    return activity


@router.delete("/{activity_id}")
def delete_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: Organizer = Depends(get_current_user)
):
    """删除活动（软删除）"""
    
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活动不存在"
        )
    
    # 检查权限
    if activity.organizer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此活动"
        )
    
    # 软删除：设置状态为已取消
    activity.status = 3
    db.commit()
    
    return {"message": "删除成功"}


@router.get("/search", response_model=List[ActivityResponse])
def search_activities(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    """搜索活动"""
    
    activities = db.query(Activity).filter(
        Activity.status == 1,  # 只搜索已发布的
        (
            Activity.activity_name.like(f"%{q}%") |
            Activity.description.like(f"%{q}%") |
            Activity.address.like(f"%{q}%")
        )
    ).all()
    
    return activities
