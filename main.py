"""
会场精灵 - FastAPI 主入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings

# 导入 API 路由
from app.api import auth, activities, sub_activities, tags, chat, upload, navigation

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="会场精灵 - 活动信息智能助手 API",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    redirect_slashes=True
)

# 配置 CORS（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录（用于上传的文件访问）
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册 API 路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(activities.router, prefix="/api/activities", tags=["活动管理"])
app.include_router(sub_activities.router, prefix="/api/sub-activities", tags=["子活动管理"])
app.include_router(tags.router, prefix="/api/tags", tags=["标签管理"])
app.include_router(chat.router, prefix="/api/chat", tags=["AI 对话"])
app.include_router(upload.router, prefix="/api/upload", tags=["文件上传"])
app.include_router(navigation.router, prefix="/api/navigation", tags=["地图导航"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用会场精灵 API",
        "docs": "/api/docs",
        "version": "1.0.0"
    }


@app.get("/api/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
