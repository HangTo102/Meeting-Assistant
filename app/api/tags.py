"""
标签管理 API
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from database.config import get_db
from database.models import ActivityTag, Activity, Organizer
from app.core.dependencies import get_current_user


router = APIRouter()


class TagCreate(BaseModel):
    """创建标签请求"""
    activity_id: int
    tag_name: str


class TagResponse(BaseModel):
    """标签响应"""
    id: int
    activity_id: int
    tag_name: str
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(
    request: TagCreate,
    db: Session = Depends(get_db),
    current_user: Organizer = Depends(get_current_user)
):
    """为活动添加标签"""
    
    # 检查活动是否存在且属于当前用户
    activity = db.query(Activity).filter(Activity.id == request.activity_id).first()
    
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活动不存在"
        )
    
    if activity.organizer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权为此活动添加标签"
        )
    
    # 检查标签是否已存在
    existing = db.query(ActivityTag).filter(
        ActivityTag.activity_id == request.activity_id,
        ActivityTag.tag_name == request.tag_name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="标签已存在"
        )
    
    tag = ActivityTag(**request.model_dump())
    
    db.add(tag)
    db.commit()
    db.refresh(tag)
    
    return tag


@router.get("/activity/{activity_id}", response_model=List[TagResponse])
def get_activity_tags(activity_id: int, db: Session = Depends(get_db)):
    """获取某活动的所有标签"""
    
    tags = db.query(ActivityTag).filter(
        ActivityTag.activity_id == activity_id
    ).all()
    
    return tags


@router.delete("/{tag_id}")
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: Organizer = Depends(get_current_user)
):
    """删除标签"""
    
    tag = db.query(ActivityTag).filter(ActivityTag.id == tag_id).first()
    
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )
    
    # 检查权限
    activity = db.query(Activity).filter(Activity.id == tag.activity_id).first()
    if activity.organizer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此标签"
        )
    
    db.delete(tag)
    db.commit()
    
    return {"message": "删除成功"}


@router.get("/all", response_model=List[str])
def get_all_tags(db: Session = Depends(get_db)):
    """获取所有标签（用于搜索建议）"""
    
    tags = db.query(ActivityTag.tag_name).distinct().all()
    
    return [tag[0] for tag in tags]
