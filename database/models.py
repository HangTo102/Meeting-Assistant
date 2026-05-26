"""
会场精灵 - 数据库模型定义
使用 SQLAlchemy ORM
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    create_engine, Column, Integer, BigInteger, String, Text, 
    DateTime, Boolean, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship, Session
from sqlalchemy.sql import func

Base = declarative_base()


class Organizer(Base):
    """主办方账户表"""
    __tablename__ = 'organizers'
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment='主办方ID')
    username = Column(String(50), nullable=False, unique=True, comment='登录用户名')
    password_hash = Column(String(255), nullable=False, comment='密码哈希(BCrypt)')
    organizer_name = Column(String(100), nullable=False, comment='主办方名称')
    contact_person = Column(String(50), nullable=True, comment='负责人姓名')
    phone = Column(String(20), nullable=False, comment='联系电话')
    email = Column(String(100), nullable=False, unique=True, comment='联系邮箱')
    address = Column(String(255), nullable=True, comment='主办方办公地址')
    status = Column(Integer, default=1, comment='状态: 0-禁用, 1-正常')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    last_login_at = Column(DateTime, nullable=True, comment='最后登录时间')
    
    # 关系
    activities = relationship("Activity", back_populates="organizer", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_status', 'status'),
        {'comment': '主办方账户表'}
    )
    
    def __repr__(self):
        return f"<Organizer(id={self.id}, username='{self.username}', name='{self.organizer_name}')>"


class Activity(Base):
    """活动详情表"""
    __tablename__ = 'activities'
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment='活动ID')
    organizer_id = Column(Integer, ForeignKey('organizers.id', ondelete='CASCADE'), nullable=False, comment='主办方ID')
    activity_name = Column(String(200), nullable=False, comment='活动完整名称')
    start_time = Column(DateTime, nullable=False, comment='开始时间')
    end_time = Column(DateTime, nullable=False, comment='结束时间')
    address = Column(String(255), nullable=False, comment='活动详细地址')
    description = Column(Text, nullable=True, comment='活动简介')
    requires_ticket = Column(Boolean, default=False, comment='是否需要购票')
    ticket_url = Column(String(500), nullable=True, comment='购票链接')
    ticket_price = Column(String(100), nullable=True, comment='票价信息')
    ticket_deadline = Column(DateTime, nullable=True, comment='购票截止时间')
    status = Column(Integer, default=1, comment='状态: 0-草稿, 1-已发布, 2-已结束, 3-已取消')
    view_count = Column(Integer, default=0, comment='浏览次数')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关系
    organizer = relationship("Organizer", back_populates="activities")
    sub_activities = relationship("SubActivity", back_populates="activity", cascade="all, delete-orphan")
    tags = relationship("ActivityTag", back_populates="activity", cascade="all, delete-orphan")
    chat_logs = relationship("ChatLog", back_populates="activity")
    
    __table_args__ = (
        Index('idx_organizer_id', 'organizer_id'),
        Index('idx_start_time', 'start_time'),
        Index('idx_status', 'status'),
        Index('idx_created_at', 'created_at'),
        {'comment': '活动详情表'}
    )
    
    def __repr__(self):
        return f"<Activity(id={self.id}, name='{self.activity_name}')>"
    
    @property
    def tag_list(self) -> List[str]:
        """获取标签列表"""
        return [tag.tag_name for tag in self.tags]
    
    @property
    def is_upcoming(self) -> bool:
        """判断活动是否即将开始"""
        return self.start_time > datetime.now()
    
    @property
    def is_ongoing(self) -> bool:
        """判断活动是否进行中"""
        now = datetime.now()
        return self.start_time <= now <= self.end_time
    
    @property
    def is_ended(self) -> bool:
        """判断活动是否已结束"""
        return self.end_time < datetime.now()


class SubActivity(Base):
    """子活动详情表"""
    __tablename__ = 'sub_activities'
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment='子活动ID')
    activity_id = Column(Integer, ForeignKey('activities.id', ondelete='CASCADE'), nullable=False, comment='所属主活动ID')
    sub_name = Column(String(200), nullable=False, comment='子活动名称')
    start_time = Column(DateTime, nullable=True, comment='开始时间')
    end_time = Column(DateTime, nullable=True, comment='结束时间')
    location = Column(String(255), nullable=True, comment='地点')
    description = Column(Text, nullable=True, comment='简介')
    sort_order = Column(Integer, default=0, comment='排序顺序')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    
    # 关系
    activity = relationship("Activity", back_populates="sub_activities")
    
    __table_args__ = (
        Index('idx_activity_id', 'activity_id'),
        Index('idx_start_time', 'start_time'),
        Index('idx_sort_order', 'sort_order'),
        {'comment': '子活动详情表'}
    )
    
    def __repr__(self):
        return f"<SubActivity(id={self.id}, name='{self.sub_name}')>"


class ActivityTag(Base):
    """活动标签表"""
    __tablename__ = 'activity_tags'
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment='标签ID')
    activity_id = Column(Integer, ForeignKey('activities.id', ondelete='CASCADE'), nullable=False, comment='活动ID')
    tag_name = Column(String(50), nullable=False, comment='标签名称')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    
    # 关系
    activity = relationship("Activity", back_populates="tags")
    
    __table_args__ = (
        UniqueConstraint('activity_id', 'tag_name', name='uk_activity_tag'),
        Index('idx_tag_name', 'tag_name'),
        {'comment': '活动标签表'}
    )
    
    def __repr__(self):
        return f"<ActivityTag(id={self.id}, tag='{self.tag_name}')>"


class ChatLog(Base):
    """匿名对话记录表"""
    __tablename__ = 'chat_logs'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='对话ID')
    session_id = Column(String(64), nullable=False, comment='匿名会话标识(UUID)')
    activity_id = Column(Integer, ForeignKey('activities.id', ondelete='SET NULL'), nullable=True, comment='关联的活动ID')
    user_message = Column(Text, nullable=False, comment='用户提问')
    assistant_response = Column(Text, nullable=True, comment='助手回答')
    response_time_ms = Column(Integer, nullable=True, comment='响应耗时(毫秒)')
    ip_address = Column(String(45), nullable=True, comment='用户IP地址')
    user_agent = Column(String(500), nullable=True, comment='用户浏览器信息')
    is_helpful = Column(Boolean, nullable=True, comment='是否有帮助: 0-否, 1-是, NULL-未评价')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    
    # 关系
    activity = relationship("Activity", back_populates="chat_logs")
    
    __table_args__ = (
        Index('idx_session_id', 'session_id'),
        Index('idx_activity_id', 'activity_id'),
        Index('idx_created_at', 'created_at'),
        {'comment': '匿名对话记录表'}
    )
    
    def __repr__(self):
        return f"<ChatLog(id={self.id}, session='{self.session_id[:8]}...')>"


class ActivityAttachment(Base):
    """活动附件表(扩展)"""
    __tablename__ = 'activity_attachments'
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment='附件ID')
    activity_id = Column(Integer, ForeignKey('activities.id', ondelete='CASCADE'), nullable=False, comment='活动ID')
    file_name = Column(String(255), nullable=False, comment='原始文件名')
    file_path = Column(String(500), nullable=False, comment='文件存储路径')
    file_size = Column(Integer, nullable=False, comment='文件大小(字节)')
    file_type = Column(String(100), nullable=False, comment='文件MIME类型')
    uploaded_by = Column(Integer, ForeignKey('organizers.id', ondelete='CASCADE'), nullable=False, comment='上传者ID')
    created_at = Column(DateTime, default=datetime.now, comment='上传时间')
    
    __table_args__ = (
        Index('idx_activity_id', 'activity_id'),
        {'comment': '活动附件表'}
    )
    
    def __repr__(self):
        return f"<ActivityAttachment(id={self.id}, file='{self.file_name}')>"


# ============================================
# 数据库连接和会话管理
# ============================================

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, database_url: str):
        self.engine = create_engine(
            database_url,
            pool_size=20,
            max_overflow=0,
            pool_pre_ping=True,
            echo=False  # 生产环境设为False
        )
        self.SessionLocal = Session
    
    def create_tables(self):
        """创建所有表"""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """删除所有表"""
        Base.metadata.drop_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """获取数据库会话"""
        return self.SessionLocal(bind=self.engine)
    
    def close(self):
        """关闭数据库连接"""
        self.engine.dispose()


# 便捷函数
def get_db_session(database_url: str) -> Session:
    """获取数据库会话的便捷函数"""
    engine = create_engine(database_url)
    return Session(bind=engine)


# ============================================
# 使用示例
# ============================================

if __name__ == "__main__":
    # 示例：本地测试
    DATABASE_URL = "mysql+pymysql://user:YOUR_PASSWORD@localhost:3306/event_assistant?charset=utf8mb4"
    
    # 创建管理器
    db = DatabaseManager(DATABASE_URL)
    
    # 创建表
    db.create_tables()
    print("✅ 数据库表创建成功！")
    
    # 示例：创建主办方
    with db.get_session() as session:
        organizer = Organizer(
            username="master",
            password_hash="$2a$10$...",  # BCrypt 哈希
            organizer_name="测试主办方",
            contact_person="管理员",
            phone="13800138000",
            email="admin@example.com"
        )
        session.add(organizer)
        session.commit()
        print(f"✅ 创建主办方: {organizer}")
