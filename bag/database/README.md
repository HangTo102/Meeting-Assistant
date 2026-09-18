# 会场精灵 - 数据库设计文档

## 📋 概述

本文档描述了会场精灵项目的数据库设计，包含4个核心表和1个扩展表。

## 🗃️ 数据表清单

| 表名 | 说明 | 记录数预估 |
|------|------|-----------|
| `organizers` | 主办方账户表 | 100-1000 |
| `activities` | 活动详情表 | 1000-10000 |
| `sub_activities` | 子活动详情表 | 5000-50000 |
| `activity_tags` | 活动标签表 | 5000-20000 |
| `chat_logs` | 匿名对话记录表 | 100000+ |
| `activity_attachments` | 活动附件表(扩展) | 10000-50000 |

---

## 1️⃣ 主办方账户表 (organizers)

### 用途
存储主办方登录账户和基本信息

### 字段说明

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | INT UNSIGNED | ✅ | 主键，自增 |
| `username` | VARCHAR(50) | ✅ | 登录用户名，唯一 |
| `password_hash` | VARCHAR(255) | ✅ | BCrypt加密后的密码 |
| `organizer_name` | VARCHAR(100) | ✅ | 主办方显示名称 |
| `contact_person` | VARCHAR(50) | ❌ | 负责人姓名 |
| `phone` | VARCHAR(20) | ✅ | 联系电话 |
| `email` | VARCHAR(100) | ✅ | 联系邮箱，唯一 |
| `address` | VARCHAR(255) | ❌ | 主办方办公地址 |
| `status` | TINYINT | ✅ | 0-禁用, 1-正常 |
| `created_at` | DATETIME | ✅ | 创建时间 |
| `updated_at` | DATETIME | ✅ | 更新时间 |
| `last_login_at` | DATETIME | ❌ | 最后登录时间 |

### 索引
- 主键: `id`
- 唯一索引: `username`, `email`
- 普通索引: `status`

---

## 2️⃣ 活动详情表 (activities)

### 用途
存储活动的基本信息、时间地点、票务等

### 字段说明

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | INT UNSIGNED | ✅ | 主键，自增 |
| `organizer_id` | INT UNSIGNED | ✅ | 主办方ID，外键 |
| `activity_name` | VARCHAR(200) | ✅ | 活动完整名称 |
| `start_time` | DATETIME | ✅ | 开始时间 |
| `end_time` | DATETIME | ✅ | 结束时间 |
| `address` | VARCHAR(255) | ✅ | 活动详细地址 |
| `description` | TEXT | ❌ | 活动简介 |
| `requires_ticket` | TINYINT(1) | ✅ | 是否需要购票 |
| `ticket_url` | VARCHAR(500) | ❌ | 购票链接 |
| `ticket_price` | VARCHAR(100) | ❌ | 票价信息文本 |
| `ticket_deadline` | DATETIME | ❌ | 购票截止时间 |
| `status` | TINYINT | ✅ | 0-草稿, 1-已发布, 2-已结束, 3-已取消 |
| `view_count` | INT UNSIGNED | ✅ | 浏览次数，默认0 |
| `created_at` | DATETIME | ✅ | 创建时间 |
| `updated_at` | DATETIME | ✅ | 更新时间 |

### 索引
- 主键: `id`
- 外键: `organizer_id`
- 普通索引: `start_time`, `status`, `created_at`

---

## 3️⃣ 子活动详情表 (sub_activities)

### 用途
存储主活动下的子活动/分会场信息

### 字段说明

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | INT UNSIGNED | ✅ | 主键，自增 |
| `activity_id` | INT UNSIGNED | ✅ | 所属主活动ID，外键 |
| `sub_name` | VARCHAR(200) | ✅ | 子活动名称 |
| `start_time` | DATETIME | ❌ | 开始时间 |
| `end_time` | DATETIME | ❌ | 结束时间 |
| `location` | VARCHAR(255) | ❌ | 具体地点/会议室 |
| `description` | TEXT | ❌ | 子活动简介 |
| `sort_order` | INT UNSIGNED | ✅ | 排序顺序，默认0 |
| `created_at` | DATETIME | ✅ | 创建时间 |

### 索引
- 主键: `id`
- 外键: `activity_id`
- 普通索引: `start_time`, `sort_order`

---

## 4️⃣ 活动标签表 (activity_tags)

### 用途
为活动打标签，便于分类和搜索

### 字段说明

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | INT UNSIGNED | ✅ | 主键，自增 |
| `activity_id` | INT UNSIGNED | ✅ | 活动ID，外键 |
| `tag_name` | VARCHAR(50) | ✅ | 标签名称 |
| `created_at` | DATETIME | ✅ | 创建时间 |

### 索引
- 主键: `id`
- 唯一索引: `activity_id` + `tag_name` (组合)
- 普通索引: `tag_name`

### 设计说明
- 采用多对多关系简化设计，不单独维护标签字典表
- 标签名直接存储，便于灵活扩展
- 可通过 `SELECT DISTINCT tag_name` 获取所有标签

---

## 5️⃣ 匿名对话记录表 (chat_logs)

### 用途
记录用户与AI助手的对话历史，用于分析优化

### 字段说明

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | BIGINT UNSIGNED | ✅ | 主键，自增 |
| `session_id` | VARCHAR(64) | ✅ | 匿名会话标识(UUID) |
| `activity_id` | INT UNSIGNED | ❌ | 关联的活动ID(可选) |
| `user_message` | TEXT | ✅ | 用户提问内容 |
| `assistant_response` | TEXT | ❌ | 助手回答内容 |
| `response_time_ms` | INT UNSIGNED | ❌ | 响应耗时毫秒 |
| `ip_address` | VARCHAR(45) | ❌ | 用户IP(支持IPv6) |
| `user_agent` | VARCHAR(500) | ❌ | 浏览器信息 |
| `is_helpful` | TINYINT(1) | ❌ | 用户反馈是否有帮助 |
| `created_at` | DATETIME | ✅ | 创建时间 |

### 索引
- 主键: `id`
- 外键: `activity_id`
- 普通索引: `session_id`, `created_at`

### 设计说明
- 使用 `BIGINT` 主键应对高并发写入场景
- `session_id` 用于关联同一用户的连续对话
- `activity_id` 可选，用于记录对话关联的具体活动
- 包含性能指标和用户反馈字段便于优化

---

## 6️⃣ 活动附件表 (activity_attachments) - 扩展

### 用途
存储活动相关的文件附件(PDF、图片等)

### 字段说明

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | INT UNSIGNED | ✅ | 主键，自增 |
| `activity_id` | INT UNSIGNED | ✅ | 活动ID，外键 |
| `file_name` | VARCHAR(255) | ✅ | 原始文件名 |
| `file_path` | VARCHAR(500) | ✅ | 文件存储路径 |
| `file_size` | INT UNSIGNED | ✅ | 文件大小(字节) |
| `file_type` | VARCHAR(100) | ✅ | MIME类型 |
| `uploaded_by` | INT UNSIGNED | ✅ | 上传者ID |
| `created_at` | DATETIME | ✅ | 上传时间 |

---

## 🔗 表关系图

```
┌─────────────────┐         ┌─────────────────┐
│   organizers    │         │   activities    │
├─────────────────┤         ├─────────────────┤
│ PK id           │◄────────┤ FK organizer_id │
│    username     │    1:N  │ PK id           │
│    password_hash│         │    activity_name│
│    organizer_name         │    start_time   │
│    ...          │         │    ...          │
└─────────────────┘         └────────┬────────┘
                                     │
                     ┌───────────────┼───────────────┐
                     │               │               │
                     ▼               ▼               ▼
            ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
            │sub_activities│ │activity_tags │ │  chat_logs   │
            ├──────────────┤ ├──────────────┤ ├──────────────┤
            │PK id         │ │PK id         │ │PK id         │
            │FK activity_id│ │FK activity_id│ │FK activity_id│
            │   sub_name   │ │   tag_name   │ │   session_id │
            │   ...        │ │   ...        │ │   ...        │
            └──────────────┘ └──────────────┘ └──────────────┘
```

---

## 📊 常用查询示例

### 1. 主办方登录验证
```sql
SELECT id, organizer_name, password_hash, status
FROM organizers
WHERE username = ? AND status = 1;
```

### 2. 获取活动列表(带标签)
```sql
SELECT 
    a.*,
    GROUP_CONCAT(at.tag_name) as tags
FROM activities a
LEFT JOIN activity_tags at ON a.id = at.activity_id
WHERE a.status = 1 
  AND a.start_time > NOW()
GROUP BY a.id
ORDER BY a.start_time ASC;
```

### 3. 获取活动详情(带子活动)
```sql
-- 主活动信息
SELECT * FROM activities WHERE id = ?;

-- 子活动列表
SELECT * FROM sub_activities 
WHERE activity_id = ? 
ORDER BY sort_order ASC, start_time ASC;

-- 标签列表
SELECT tag_name FROM activity_tags WHERE activity_id = ?;
```

### 4. 搜索活动
```sql
SELECT DISTINCT a.*
FROM activities a
LEFT JOIN activity_tags at ON a.id = at.activity_id
WHERE a.status = 1
  AND (
    a.activity_name LIKE '%?%' 
    OR a.description LIKE '%?%'
    OR a.address LIKE '%?%'
    OR at.tag_name = '?'
  )
ORDER BY a.start_time ASC;
```

### 5. 获取会话历史记录
```sql
SELECT user_message, assistant_response, created_at
FROM chat_logs
WHERE session_id = ?
ORDER BY created_at ASC
LIMIT 50;
```

### 6. 统计查询示例
```sql
-- 今日新增对话数
SELECT COUNT(*) FROM chat_logs 
WHERE DATE(created_at) = CURDATE();

-- 热门活动排行
SELECT a.activity_name, COUNT(c.id) as chat_count
FROM activities a
LEFT JOIN chat_logs c ON a.id = c.activity_id
GROUP BY a.id
ORDER BY chat_count DESC
LIMIT 10;
```

---

## ⚙️ 技术规范

### 字符集
- 默认使用 `utf8mb4` 支持 emoji 和完整 Unicode
- 排序规则 `utf8mb4_unicode_ci`

### 存储引擎
- 全部使用 `InnoDB` 支持事务和外键

### 时间字段
- 统一使用 `DATETIME` 类型
- 默认 `CURRENT_TIMESTAMP`
- 自动更新使用 `ON UPDATE CURRENT_TIMESTAMP`

### 软删除
- 本项目不使用物理删除，通过 `status` 字段控制状态
- 关联删除使用外键级联

---

## 🚀 部署建议

### MySQL 版本
- 推荐 MySQL 8.0+ 或 MariaDB 10.5+

### 连接池配置
```properties
# 示例配置
spring.datasource.hikari.maximum-pool-size=20
spring.datasource.hikari.minimum-idle=5
spring.datasource.hikari.connection-timeout=30000
```

### 备份策略
- 每日全量备份
- 实时 binlog 备份
- 重点表: `activities`, `chat_logs`

---

## 📝 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0 | 2026-03-30 | 初始版本，包含4个核心表 |
