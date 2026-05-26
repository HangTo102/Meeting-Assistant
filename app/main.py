"""
会场精灵 - 应用主入口
使用 FastAPI 框架
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# 导入自己的模块
from app.database.config import get_db
from app.api import auth, activities, navigation, chat, sub_activities, tags, upload

# 创建 FastAPI 应用
app = FastAPI(
    title="会场精灵 API",
    description="活动信息智能助手后台接口",
    version="1.0.0",
    docs_url="/api/docs",  # API文档地址
    redoc_url="/api/redoc",  # ReDoc文档地址
    openapi_url="/api/openapi.json"  # OpenAPI规范地址
)

# 配置CORS（跨域资源共享）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境要指定具体域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有HTTP头
)

# 包含路由
app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["认证"],
    dependencies=[Depends(get_db)]  # 依赖数据库会话
)

app.include_router(
    activities.router,
    prefix="/api/activities",
    tags=["活动管理"]
)

app.include_router(
    navigation.router,
    prefix="/api/navigation",
    tags=["地图导航"]
)

app.include_router(
    chat.router,
    prefix="/api/chat",
    tags=["AI 对话"]
)

app.include_router(
    sub_activities.router,
    prefix="/api/sub-activities",
    tags=["子活动管理"]
)

app.include_router(
    tags.router,
    prefix="/api/tags",
    tags=["标签管理"]
)

app.include_router(
    upload.router,
    prefix="/api/upload",
    tags=["文件上传"]
)

# 根路由
@app.get("/")
async def root():
    """健康检查接口"""
    return {
        "name": "会场精灵 API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "status": "running"
    }

# 健康检查
@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}

# 测试数据库连接
@app.get("/test-db")
async def test_db(db: Session = Depends(get_db)):
    """测试数据库连接"""
    try:
        # 简单查询测试
        result = db.execute("SELECT 1")
        return {"status": "connected", "result": result.fetchone()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库连接失败: {str(e)}")