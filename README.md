# 会场精灵 (Meeting Assistant) v2.0

> 基于活动信息的智能问答助手 —— 让活动信息触手可及

---

## 项目简介

一个基于活动信息的智能问答助手，支持查询活动的时间、地点、票务、阵容、参展信息等内容。

本项目旨在解决由于主办方信息发布不醒目、用户接收消息不及时等问题。主办方提交活动信息至本系统后，用户可通过 AI 智能问答、地图导航等方式快速获取所需信息。

---

## ✨ 功能特性

### v2.0 全新升级

- **全新架构**：后端 FastAPI + 前端 Vue 3，告别 Streamlit 平台限制
- **MySQL 数据库**：结构化存储，支持完整的活动/子活动/标签管理
- **主办方管理系统**：独立的注册/登录/上传/修改入口
- **高德地图动态导航**：实时路线规划，支持驾车/公交/步行多种出行方式
- **AI 智能问答**：接入通义千问 API，精准识别活动相关问题
- **JWT 认证**：安全的 Token 鉴权机制
- **文件上传**：支持活动附件（PDF、Word、Excel 等）
- **RESTful API**：完整的 API 文档（自动生成 Swagger/Redoc）

### 功能清单

| 模块 | 功能 | 状态 |
|------|------|------|
| 💬 AI 对话 | 智能识别活动问题，精准回答 | ✅ |
| 📋 活动管理 | 活动/子活动/标签 CRUD | ✅ |
| 🏢 主办方 | 注册、登录、信息管理 | ✅ |
| 🗺️ 地图导航 | 高德地图动态路线规划 | ✅ |
| 📎 文件上传 | 活动附件上传管理 | ✅ |
| 🔐 认证鉴权 | JWT Token 安全认证 | ✅ |

---

## 🏗️ 技术架构

```
用户 (Web 浏览器)
    ↓
Vue 3 前端 (Element Plus)
    ↓
FastAPI RESTful API
    ↓
SQLAlchemy ORM
    ↓
MySQL 数据库
```

### 外部服务集成

- **AI 服务**：阿里云 DashScope (通义千问)
- **地图服务**：高德地图 JavaScript API
- **认证方式**：JWT (python-jose) + bcrypt 密码哈希

---

## 🚀 快速启动

### 前置要求

- Python 3.10+
- Node.js 20+
- MySQL 8.0+

### 1. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env，填入实际配置
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/event_assistant?charset=utf8mb4
SECRET_KEY=YOUR_JWT_SECRET
DASHSCOPE_API_KEY=YOUR_DASHSCOPE_API_KEY    # AI 服务（可选）
AMAP_API_KEY=YOUR_AMAP_API_KEY              # 地图服务（可选）
```

### 2. 初始化数据库

```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE event_assistant CHARACTER SET utf8mb4;"

# 导入表结构
mysql -u root -p event_assistant < database/schema.sql

# 或使用 Python 脚本初始化（含示例数据）
python database/init_db.py
```

### 3. 一键启动

```bash
# 会自动配置虚拟环境、安装依赖、启动前后端
bash run.sh
```

### 4. 手动启动

```bash
# 后端
cd SH-AIv2
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
# 访问 http://localhost:8000/api/docs

# 前端
cd frontend
npm install
npm run dev
# 访问 http://localhost:5173
```

---

## 📁 项目结构

```
SH-AIv2/
├── main.py                 # FastAPI 应用入口
├── app/                    # 后端核心代码
│   ├── api/               # API 路由（认证/活动/对话/导航等）
│   ├── core/              # 配置、安全、依赖注入
│   ├── schemas/           # Pydantic 数据验证
│   └── services/          # 业务逻辑（AI 服务/检索）
├── database/               # 数据库层
│   ├── models.py          # SQLAlchemy ORM 模型
│   ├── config.py          # 数据库连接配置
│   └── init_db.py         # 初始化脚本
├── frontend/               # Vue 3 前端
│   └── src/
│       ├── api/           # Axios API 客户端
│       ├── stores/        # Pinia 状态管理
│       └── views/         # 页面组件
├── static/                 # 静态文件/上传目录
├── requirements.txt        # Python 依赖
└── run.sh                  # 一键启动脚本
```

---

## 📖 API 文档

启动后端后访问：

- Swagger UI: `http://localhost:8000/api/docs`
- Redoc: `http://localhost:8000/api/redoc`

### 主要接口

| 路径 | 方法 | 说明 |
|------|------|------|
| `/api/auth/register` | POST | 主办方注册 |
| `/api/auth/login` | POST | 主办方登录 |
| `/api/activities` | GET/POST | 活动列表/创建 |
| `/api/activities/{id}` | GET/PUT/DELETE | 活动详情/编辑/删除 |
| `/api/sub-activities` | GET/POST | 子活动管理 |
| `/api/tags` | GET/POST | 标签管理 |
| `/api/chat/send` | POST | AI 对话 |
| `/api/upload/file` | POST | 文件上传 |
| `/api/navigation/route` | POST | 路线规划 |

---

## 📝 版本历史

### v1.x (旧版)
- Streamlit 轻量架构，JSON 数据源
- 基础 AI 问答功能
- 静态地图导航（受 Streamlit iframe 限制）

### v2.0 (当前)
- **全新架构**：FastAPI + Vue 3 + MySQL，彻底解决平台限制
- **主办方管理系统**：独立的账号认证与管理
- **动态地图导航**：基于高德地图 API 的实时路线规划
- **结构化数据存储**：活动/子活动/标签/附件完整管理
- **完善的文件上传**：支持多种格式的活动附件
- **自动生成 API 文档**：Swagger + Redoc
- **更安全的认证**：JWT + bcrypt 密码哈希

---

## ⚠️ 注意事项

1. **API 密钥安全**：`.env` 文件已配置 `.gitignore`，请勿手动移除保护
2. **生产部署**：请修改默认的 JWT SECRET_KEY，使用强密码
3. **地图服务**：需要自行申请高德地图 Web API Key
4. **AI 服务**：需要自行申请阿里云 DashScope API Key

---

## 🐛 常见问题

### 数据库连接失败
检查 `.env` 中的 `DATABASE_URL` 是否正确，确认 MySQL 服务已启动。

### 前端无法连接后端
1. 确认后端已启动且端口未被占用
2. 检查 `frontend/.env` 中的 `VITE_API_BASE_URL`
3. 检查浏览器控制台 CORS 错误信息

### AI 对话不工作
确认 `.env` 中已配置 `DASHSCOPE_API_KEY`，且账户有可用额度。

---

*本项目仅用作学习交流使用*
