"""
文件上传 API
"""
import os
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from database.config import get_db
from database.models import ActivityAttachment, Activity, Organizer
from app.core.dependencies import get_current_user
from app.core.config import settings


router = APIRouter()


class UploadResponse(BaseModel):
    """上传响应"""
    file_id: int
    file_name: str
    file_url: str
    file_size: int
    file_type: str


def validate_file_extension(filename: str) -> bool:
    """验证文件扩展名"""
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    return ext in settings.ALLOWED_EXTENSIONS


@router.post("/", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    activity_id: int = None,
    db: Session = Depends(get_db),
    current_user: Organizer = Depends(get_current_user)
):
    """上传文件"""
    
    # 验证文件类型
    if not validate_file_extension(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型，仅支持：{', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # 生成唯一文件名
    file_ext = file.filename.rsplit('.', 1)[-1] if '.' in file.filename else ''
    unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
    
    # 创建上传目录
    upload_dir = Path(settings.UPLOAD_FOLDER)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存文件
    file_path = upload_dir / unique_filename
    
    try:
        # 分块读取并检查文件大小，避免大文件一次性载入内存
        total_size = 0
        with open(file_path, "wb") as f:
            while True:
                chunk = await file.read(1024 * 1024)  # 每次读 1MB
                if not chunk:
                    break
                total_size += len(chunk)
                if total_size > settings.MAX_UPLOAD_SIZE:
                    f.close()
                    os.remove(file_path)
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"文件过大，最大支持 {settings.MAX_UPLOAD_SIZE // 1024 // 1024}MB"
                    )
                f.write(chunk)
        
    except HTTPException:
        raise
    except Exception as e:
        if file_path.exists():
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传失败：{str(e)}"
        )
    
    # 如果关联活动，验证权限
    if activity_id:
        activity = db.query(Activity).filter(Activity.id == activity_id).first()
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="活动不存在"
            )
        if activity.organizer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权为此活动上传文件"
            )
    
    # 保存数据库记录（未关联活动时 activity_id 置为 NULL）
    attachment = ActivityAttachment(
        activity_id=activity_id,
        file_name=file.filename,
        file_path=str(file_path),
        file_size=total_size,
        file_type=file.content_type or "application/octet-stream",
        uploaded_by=current_user.id
    )
    
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    
    return UploadResponse(
        file_id=attachment.id,
        file_name=file.filename,
        file_url=f"/static/uploads/{unique_filename}",
        file_size=total_size,
        file_type=file.content_type or "application/octet-stream"
    )


@router.get("/{file_id}")
async def get_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: Organizer = Depends(get_current_user)
):
    """获取文件"""
    
    attachment = db.query(ActivityAttachment).filter(
        ActivityAttachment.id == file_id
    ).first()
    
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    # 检查权限
    activity = db.query(Activity).filter(Activity.id == attachment.activity_id).first()
    if activity and activity.organizer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此文件"
        )
    
    if not os.path.exists(attachment.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件已丢失"
        )
    
    return FileResponse(
        attachment.file_path,
        filename=attachment.file_name,
        media_type=attachment.file_type
    )


@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: Organizer = Depends(get_current_user)
):
    """删除文件"""
    
    attachment = db.query(ActivityAttachment).filter(
        ActivityAttachment.id == file_id
    ).first()
    
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    # 检查权限
    activity = db.query(Activity).filter(Activity.id == attachment.activity_id).first()
    if activity and activity.organizer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此文件"
        )
    
    # 删除文件
    try:
        if os.path.exists(attachment.file_path):
            os.remove(attachment.file_path)
    except Exception as e:
        pass  # 文件删除失败不影响数据库操作
    
    # 删除数据库记录
    db.delete(attachment)
    db.commit()
    
    return {"message": "删除成功"}
