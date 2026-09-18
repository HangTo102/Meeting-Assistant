"""
数据库配置
基于现有的 database/config.py，适配FastAPI依赖注入
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库连接URL
DATABASE_URL = os.getenv("DATABASE_URL", "")

# SQLAlchemy引擎配置
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=0,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True,
    echo=False,
)

# 会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    """
    FastAPI依赖注入：获取数据库会话
    
    使用示例：
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            items = db.query(Item).all()
            return items
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 测试连接
def test_connection():
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print(f"✅ 数据库连接成功！")
            print(f"   URL: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")
            return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

if __name__ == "__main__":
    test_connection()