"""
数据库模型导入
为了方便使用，直接从现有的 models.py 导入
"""

# 直接从现有的 models.py 导入所有模型
from database.models import (
    Base,  # SQLAlchemy基类
    Organizer,  # 主办方
    Activity,  # 活动
    SubActivity,  # 子活动
    ActivityTag,  # 标签
    ChatLog,  # 对话记录
    ActivityAttachment,  # 附件
    DatabaseManager,  # 数据库管理器
    get_db_session  # 获取会话的便捷函数
)

# 重新导出，方便引用
__all__ = [
    'Base',
    'Organizer',
    'Activity',
    'SubActivity',
    'ActivityTag',
    'ChatLog',
    'ActivityAttachment',
    'DatabaseManager',
    'get_db_session'
]