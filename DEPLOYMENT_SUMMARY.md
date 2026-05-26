# 部署总结文档

> 基于阿里云 ECS Ubuntu 20.04 的实际部署过程

---

## 一、首次部署步骤

### 1. 环境准备（仅首次需要）

```bash
# 安装基础环境
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip nginx mysql-server mysql-client supervisor ufw

# 安装 Node.js（用于构建前端）
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -
sudo apt install -y nodejs

# 启动 MySQL
sudo systemctl start mysql
sudo systemctl enable mysql
```

### 2. MySQL 配置

```bash
# 修改 root 认证方式（Ubuntu 默认用 auth_socket，改为密码认证）
sudo mysql

# 在 MySQL 命令行执行：
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '你的密码';
FLUSH PRIVILEGES;
EXIT;

# 创建数据库
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS event_assistant DEFAULT CHARACTER SET utf8mb4;"
```

### 3. 上传项目文件

方法一：SCP（推荐，项目未使用 Git 时）
```bash
# 本地执行
scp -r /本地项目路径/sh-ai ecs-user@<YOUR_SERVER_IP>:~/sh-ai
```

方法二：Git
```bash
# 在服务器上
git clone <仓库地址> ~/sh-ai
```

### 4. 配置项目

```bash
cd ~/sh-ai

# · 修改 .env 中的数据库密码
# · 修改 database/.env 中的数据库密码
# · 前端 frontend/.env.production 中 VITE_API_BASE_URL=/api（已正确）

# 创建虚拟环境并安装依赖
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. 初始化数据库

```bash
# 导入表结构
mysql -u root -p event_assistant < ~/sh-ai/database/schema.sql

# 删除占位符账号（password_hash 是假的）
mysql -u root -p -e "DELETE FROM event_assistant.organizers;"

# 生成正确的 bcrypt 密码哈希
cd ~/sh-ai && venv/bin/python -c "
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
print(pwd_context.hash('YOUR_SECURE_PASSWORD'))
"

# 用得到的哈希值插入管理员（将 HASH_HERE 替换为实际值）
mysql -u root -p -e "
INSERT INTO event_assistant.organizers
(username, password_hash, organizer_name, contact_person, phone, email, address, status)
VALUES ('master', 'HASH_HERE', '测试主办方', '管理员', '13800138000', 'admin@example.com', '上海市浦东新区测试地址', 1);
"
```

### 6. 构建前端

```bash
cd ~/sh-ai/frontend
npm install
npm run build
```

### 7. 配置 Nginx

```bash
sudo cp ~/sh-ai/deploy/nginx.conf /etc/nginx/sites-available/sh-ai
sudo ln -s /etc/nginx/sites-available/sh-ai /etc/nginx/sites-enabled/

# 复制前端构建产物和静态文件
sudo mkdir -p /var/www/sh-ai
sudo cp -r ~/sh-ai/frontend/dist /var/www/sh-ai/frontend/
sudo cp -r ~/sh-ai/static /var/www/sh-ai/

# 检查配置并重启 Nginx
sudo nginx -t && sudo systemctl restart nginx
```

### 8. 防火墙

```bash
sudo ufw allow 22/tcp     # SSH
sudo ufw allow 80/tcp     # HTTP
sudo ufw allow 443/tcp    # HTTPS（未来用）
sudo ufw allow 8000/tcp   # 后端直连（调试用，可不开）
sudo ufw --force enable
```

### 9. 配置 Supervisor（进程守护，终端关闭后服务不停）

```bash
sudo cp ~/sh-ai/deploy/supervisor.conf /etc/supervisor/conf.d/sh-ai.conf
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start sh-ai
sudo supervisorctl status sh-ai
```

### 10. 验证

```bash
curl http://127.0.0.1/api/health
# 返回: {"status":"ok","version":"1.0.0"}

curl -X POST http://127.0.0.1/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"master","password":"YOUR_PASSWORD"}'
# 应返回包含 access_token 的 JSON
```

浏览器访问 `http://服务器公网IP`，应该能正常打开。

---

## 二、关于域名和备案

### 当前阶段（开发/测试用）——不需要

直接用服务器公网 IP 地址访问即可，无需域名和备案。

### 正式上线需要

| 项目 | 说明 | 费用 |
|------|------|------|
| **域名** | 阿里云万网购买，如 `example.com` | ≈ ¥30-80/年 |
| **ICP 备案（必办）** | 阿里云免费代办，耗时约 5-20 个工作日 | 免费 |
| **SSL 证书（推荐）** | 阿里云免费单域名证书 / Let's Encrypt | 免费 |
| **公安备案** | ICP 备案通过后还需公安备案 | 免费 |

**流程**：买域名 → ICP 备案 → 配置 DNS（解析到 ECS IP）→ 申请 SSL 证书 → 配置 Nginx HTTPS → 公安备案

**注意事项**：
- 备案期间服务器不能关
- 域名必须实名认证后才能备案
- 未备案域名阿里云会拦截 80/443 端口

---

## 三、后续代码更新的操作方法

> 当前项目未使用 Git 管理，推荐以下两种方式

### 方案 A：SCP 手动上传（简单直接）

```bash
# 本地开发机执行，每次改完后运行：

# 1. 上传变更的文件
scp -r main.py ecs-user@<YOUR_SERVER_IP>:~/sh-ai/
scp -r app/ ecs-user@<YOUR_SERVER_IP>:~/sh-ai/
scp -r database/ ecs-user@<YOUR_SERVER_IP>:~/sh-ai/

# 2. 如果改了前端
cd frontend && npm run build
scp -r dist/* ecs-user@<YOUR_SERVER_IP>:/var/www/sh-ai/frontend/dist/

# 3. 重启服务
ssh ecs-user@<YOUR_SERVER_IP> "sudo supervisorctl restart sh-ai && sudo systemctl reload nginx"
```

### 方案 B：Git（推荐，可追踪版本）

**步骤 1** — 本地初始化仓库并推送
```bash
# 本地项目目录
cd sh-ai
git init
git add .
git commit -m "初始化"
# 在 GitHub / Gitee 上创建私有仓库后：
git remote add origin <仓库地址>
git push -u origin main
```

**步骤 2** — 服务器拉取
```bash
# 服务器上
cd ~/sh-ai
git init
git remote add origin <仓库地址>
git pull origin main
```

**步骤 3** — 日常更新
```bash
# 本地修改 → commit → push
git add .
git commit -m "改了什么"
git push

# 服务器拉取并重启
ssh ecs-user@<YOUR_SERVER_IP> "
  cd ~/sh-ai && git pull && source venv/bin/activate && pip install -r requirements.txt &&
  sudo supervisorctl restart sh-ai
"

# 如果前端有改动，再加：
ssh ecs-user@<YOUR_SERVER_IP> "
  cd ~/sh-ai/frontend && npm install && npm run build &&
  sudo cp -r dist/* /var/www/sh-ai/frontend/dist/ &&
  sudo systemctl reload nginx
"
```

### 重启服务的命令速查

```bash
# 后端（Supervisor 管理）
sudo supervisorctl restart sh-ai
sudo supervisorctl status sh-ai

# 前端（Nginx）
sudo systemctl reload nginx

# 查看日志
sudo supervisorctl tail -f sh-ai          # 后端日志
tail -f ~/sh-ai/backend.log               # 无 Supervisior 时的日志
sudo tail -f /var/log/nginx/sh-ai-error.log  # Nginx 错误日志
```

---

## 四、账号信息

初始主办方账号信息请通过数据库初始化脚本创建，生产环境请务必修改默认密码。

---

## 五、项目结构速查

```
~/sh-ai/
├── main.py              # 后端入口
├── app/                 # 后端代码
│   ├── api/             # API 路由
│   └── core/            # 配置 + 安全
├── frontend/            # Vue 3 前端源码
├── database/            # 数据库模型 + 初始化
├── deploy/              # 部署配置（Nginx, Supervisor）
└── static/uploads/      # 上传文件存储
```
