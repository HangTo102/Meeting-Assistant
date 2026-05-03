"""
子活动管理 API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from database.config import get_db
from database.models import SubActivity, Activity, Organizer
from app.core.dependencies import get_current_user


router = APIRouter()


class SubActivityCreate(BaseModel):
    """创建子活动请求"""
    activity_id: int
    sub_name: str
    start_time: datetime = None
    end_time: datetime = None
    location: str = None
    description: str = None
    sort_order: int = 0


class SubActivityUpdate(BaseModel):
    """更新子活动请求"""
    sub_name: str = None
    start_time: datetime = None
    end_time: datetime = None
    location: str = None
    description: str = None
    sort_order: int = None


class SubActivityResponse(BaseModel):
    """子活动响应"""
    id: int
    activity_id: int
    sub_name: str
    start_time: datetime = None
    end_time: datetime = None
    location: str = None
    description: str = None
    sort_order: int
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/", response_model=SubActivityResponse, status_code=status.HTTP_201_CREATED)
def create_sub_activity(
    request: SubActivityCreate,
    db: Session = Depends(get_db),
    current_user: Organizer = Depends(get_current_user)
):
    """创建子活动"""
    
    # 检查主活动是否存在且属于当前用户
    activity = db.query(Activity).filter(
        Activity.id == request.activity_id
    ).first()
    
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="主活动不存在"
        )
    
    if activity.organizer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权为此活动添加子活动"
        )
    
    sub_activity = SubActivity(**request.model_dump())
    
    db.add(sub_activity)
    db.commit()
    db.refresh(sub_activity)
    
    return sub_activity


@router.get("/activity/{activity_id}", response_model=List[SubActivityResponse])
def get_sub_activities(activity_id: int, db: Session = Depends(get_db)):
    """获取某活动的所有子活动"""
    
    sub_activities = db.query(SubActivity).filter(
        SubActivity.activity_id == activity_id
    ).order_by(SubActivity.sort_order, SubActivity.start_time).all()
    
    return sub_activities


@router.put("/{sub_activity_id}", response_model=SubActivityResponse)
def update_sub_activity(
    sub_activity_id: int,
    request: SubActivityUpdate,
    db: Session = Depends(get_db),
    current_user: Organizer = Depends(get_current_user)
):
    """更新子活动"""
    
    sub_activity = db.query(SubActivity).filter(
        SubActivity.id == sub_activity_id
    ).first()
    
    if not sub_activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="子活动不存在"
        )
    
    # 检查权限
    activity = db.query(Activity).filter(Activity.id == sub_activity.activity_id).first()
    if activity.organizer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此子活动"
        )
    
    # 更新字段
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sub_activity, field, value)
    
    db.commit()
    db.refresh(sub_activity)
    
    return sub_activity


@router.delete("/{sub_activity_id}")
def delete_sub_activity(
    sub_activity_id: int,
    db: Session = Depends(get_db),
    current_user: Organizer = Depends(get_current_user)
):
    """删除子活动"""
    
    sub_activity = db.query(SubActivity).filter(
        SubActivity.id == sub_activity_id
    ).first()
    
    if not sub_activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="子活动不存在"
        )
    
    # 检查权限
    activity = db.query(Activity).filter(Activity.id == sub_activity.activity_id).first()
    if activity.organizer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此子活动"
        )
    
    db.delete(sub_activity)
    db.commit()
    
    return {"message": "删除成功"}
