# 会场精灵 - 快速启动指南

## 📁 项目结构

```
SH-AIv2/
├── main.py                 # FastAPI 后端入口
├── app/                    # 后端代码
│   ├── api/               # API 路由
│   ├── core/              # 核心配置
│   ├── models/            # 数据模型
│   ├── schemas/           # 数据验证
│   └── services/          # 业务逻辑
├── database/              # 数据库配置和模型
├── frontend/              # Vue3 前端项目
└── static/uploads/        # 上传文件存储
```

## 🚀 快速启动

### 1. 启动数据库

```bash
# 确保 MySQL 已安装并运行
mysql -u root -p

# 创建数据库
CREATE DATABASE event_assistant CHARACTER SET utf8mb4;
exit

# 导入表结构
cd /path/to/SH-AIv2
mysql -u root -p event_assistant < database/schema.sql
```

### 2. 启动后端

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 启动后端服务（开发模式）
python main.py
```

后端将运行在：http://localhost:8000  
API 文档：http://localhost:8000/api/docs

### 3. 启动前端

```bash
cd frontend

# 安装依赖（如果还没安装）
npm install

# 启动开发服务器
npm run dev
```

前端将运行在：http://localhost:5173

## 📝 测试账号

使用注册功能创建新账号，或使用测试数据中的账号登录。

## 🔧 配置

### 后端配置 (.env)

```bash
DATABASE_URL=mysql+pymysql://root:你的密码@localhost:3306/event_assistant?charset=utf8mb4
SECRET_KEY=your-secret-key
DASHSCOPE_API_KEY=你的通义千问 API Key（可选）
```

### 前端配置 (frontend/.env)

```bash
VITE_API_BASE_URL=http://localhost:8000/api
```

## 🎯 功能清单

### ✅ 已完成
- [x] 用户注册/登录
- [x] JWT Token 认证
- [x] 活动 CRUD
- [x] 子活动管理
- [x] 标签管理
- [x] AI 对话（需配置 API Key）
- [x] 文件上传

### ⏳ 待完善
- [ ] 活动搜索优化
- [ ] 数据可视化统计
- [ ] 移动端适配
- [ ] 权限细化

## 🐛 常见问题

### 数据库连接失败
检查 `database/config.py` 中的数据库密码是否正确

### 前端无法连接后端
1. 确认后端已启动
2. 检查 `frontend/.env` 中的 API 地址
3. 检查浏览器控制台是否有 CORS 错误

### AI 对话不工作
配置通义千问 API Key：
```bash
export DASHSCOPE_API_KEY=your_key
```
