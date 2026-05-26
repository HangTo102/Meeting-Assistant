# 会场精灵数据库模块

## 📁 文件结构

```
database/
├── README.md              # 数据库设计文档
├── schema.sql             # SQL 建表脚本
├── models.py              # SQLAlchemy ORM 模型
├── config.py.example      # 数据库配置示例
├── .env.example           # 环境变量示例
├── requirements.txt       # Python 依赖
└── init_db.py             # 数据库初始化脚本
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 创建数据库

```bash
# MySQL 命令行
mysql -u root -p

# 执行 SQL
CREATE DATABASE event_assistant CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. 配置连接

```bash
# 复制配置文件
cp config.py.example config.py

# 编辑 config.py，设置数据库连接信息
```

### 4. 初始化数据

```bash
# 方法1: 使用 Python 脚本
python init_db.py --drop

# 方法2: 使用 SQL 脚本
mysql -u root -p event_assistant < schema.sql
```

## 📋 数据表

| 表名 | 说明 |
|------|------|
| `organizers` | 主办方账户 |
| `activities` | 活动详情 |
| `sub_activities` | 子活动详情 |
| `activity_tags` | 活动标签 |
| `chat_logs` | 匿名对话记录 |
| `activity_attachments` | 活动附件(扩展) |

## 💻 使用示例

### 连接数据库

```python
from database.config import SessionLocal

# 获取会话
db = SessionLocal()

# 使用...
db.close()
```

### 查询数据

```python
from database.models import Activity, Organizer
from database.config import SessionLocal

db = SessionLocal()

# 查询所有活动
activities = db.query(Activity).all()

# 查询特定主办方活动
organizer = db.query(Organizer).filter_by(username="master").first()
activities = organizer.activities

db.close()
```

### 创建数据

```python
from database.models import Activity, Organizer
from database.config import SessionLocal
from datetime import datetime

db = SessionLocal()

# 创建主办方
organizer = Organizer(
    username="new_org",
    password_hash="hashed_password",
    organizer_name="新主办方",
    phone="13800138000",
    email="org@example.com"
)
db.add(organizer)
db.commit()

# 创建活动
activity = Activity(
    organizer_id=organizer.id,
    activity_name="新活动",
    start_time=datetime(2026, 5, 1, 9, 0),
    end_time=datetime(2026, 5, 1, 18, 0),
    address="活动地址"
)
db.add(activity)
db.commit()

db.close()
```

## 🔧 常用命令

```bash
# 初始化数据库 (带示例数据)
python init_db.py

# 重新初始化 (删除现有表)
python init_db.py --drop

# 仅创建表结构，不插入数据
python init_db.py --no-data

# 测试数据库连接
python config.py
```

## 📝 注意事项

1. **字符集**: 所有表使用 `utf8mb4` 支持 emoji
2. **时区**: 数据库时间使用 UTC 或本地时区统一
3. **密码**: 生产环境必须使用 BCrypt 加密
4. **备份**: 建议每日备份 `activities` 和 `chat_logs` 表
