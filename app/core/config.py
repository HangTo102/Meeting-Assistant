"""
应用配置
"""
import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用配置"""
    
    PROJECT_NAME: str = "会场精灵"
    VERSION: str = "2.0.0"
    API_PREFIX: str = "/api"
    DEBUG: bool = False
    PORT: int = 8000
    
    # CORS 配置
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    
    # 数据库配置（从 .env 读取）
    DATABASE_URL: str = ""
    
    # JWT 配置（从 .env 读取）
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    
    # 文件上传配置
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024
    UPLOAD_FOLDER: str = "static/uploads"
    ALLOWED_EXTENSIONS: set = {"pdf", "png", "jpg", "jpeg", "gif", "doc", "docx"}
    
    # AI 配置
    DASHSCOPE_API_KEY: str = ""
    AI_MODEL: str = "qwen-plus"
    
    # 高德地图配置
    AMAP_API_KEY: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


settings = Settings()
