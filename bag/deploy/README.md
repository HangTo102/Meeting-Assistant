# 会场精灵部署说明

## 一、Docker Compose 一键部署（推荐开发/演示）

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 DATABASE_URL、SECRET_KEY、DASHSCOPE_API_KEY、AMAP_API_KEY 等

# 2. 构建并启动
docker-compose up --build -d

# 3. 初始化数据库（首次）
docker-compose exec mysql mysql -uroot -p${DB_ROOT_PASSWORD} -e "CREATE DATABASE IF NOT EXISTS ${DB_NAME} DEFAULT CHARACTER SET utf8mb4;"
docker-compose exec -T mysql mysql -uroot -p${DB_ROOT_PASSWORD} ${DB_NAME} < database/schema.sql

# 4. 查看状态
docker-compose ps
docker-compose logs -f backend
```

访问: http://localhost

## 二、传统服务器部署（生产环境）

### 2.1 准备

1. 将项目上传到 `/root/sh-ai/`。
2. 复制并编辑 `.env`：
   ```bash
   cd /root/sh-ai
   cp .env.example .env
   vim .env
   ```
3. 确保 `database/schema.sql` 存在。

### 2.2 首次安装

```bash
bash deploy/install.sh
```

脚本会自动完成：
- 安装 Python 3.11、Nginx、MySQL、Supervisor
- 配置 Swap
- 创建数据库并导入表结构
- 创建虚拟环境并安装依赖
- 构建前端
- 部署静态文件
- 配置 Nginx 和 Supervisor

### 2.3 日常更新

```bash
bash deploy/update.sh
```

### 2.4 切换 HTTPS（域名备案后）

1. 申请证书：
   ```bash
   # Alibaba Cloud Linux / CentOS
   dnf install -y certbot python3-certbot-nginx
   certbot --nginx -d yourdomain.com
   ```
2. 或手动替换 Nginx 配置：
   ```bash
   cp deploy/nginx-https.conf /etc/nginx/conf.d/sh-ai.conf
   # 将 yourdomain.com 替换为真实域名，并配置证书路径
   nginx -t && systemctl reload nginx
   ```

## 三、部署文件清单

| 文件 | 作用 |
|------|------|
| `Dockerfile` | 后端镜像构建 |
| `docker-compose.yml` | Docker Compose 编排 |
| `docker/nginx.conf` | 容器内 Nginx 配置 |
| `deploy/install.sh` | 服务器首次安装脚本 |
| `deploy/update.sh` | 服务器更新脚本 |
| `deploy/nginx-http.conf` | HTTP 版 Nginx 配置 |
| `deploy/nginx-https.conf` | HTTPS 版 Nginx 配置 |
| `deploy/supervisor.ini` | Supervisor 配置模板 |
