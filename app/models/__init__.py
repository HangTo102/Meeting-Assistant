# 从 database 目录导入模型
import sys
from pathlib import Path

# 添加项目根目录到路径
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from database.models import Organizer, Activity, SubActivity, ActivityTag, ChatLog, ActivityAttachment

__all__ = [
    "Organizer",
    "Activity",
    "SubActivity",
    "ActivityTag",
    "ChatLog",
    "ActivityAttachment"
]
