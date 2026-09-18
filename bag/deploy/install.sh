#!/bin/bash
set -e

# 会场精灵 - 首次部署脚本
# 支持 Alibaba Cloud Linux 3 / CentOS / Ubuntu / Debian

PROJECT_NAME="sh-ai"
PROJECT_DIR="/root/${PROJECT_NAME}"
WWW_DIR="/var/www/${PROJECT_NAME}"
NGINX_CONF_DIR=""
SUPERVISOR_CONF_DIR=""
PYTHON_BIN="python3"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VERSION=$VERSION_ID
    else
        log "无法检测操作系统"
        exit 1
    fi
    log "检测到系统: $OS $VERSION"
}

detect_paths() {
    if [ -d /etc/nginx/conf.d ]; then
        NGINX_CONF_DIR="/etc/nginx/conf.d"
    elif [ -d /etc/nginx/sites-available ]; then
        NGINX_CONF_DIR="/etc/nginx/sites-available"
    fi

    if [ -d /etc/supervisord.d ]; then
        SUPERVISOR_CONF_DIR="/etc/supervisord.d"
    elif [ -d /etc/supervisor/conf.d ]; then
        SUPERVISOR_CONF_DIR="/etc/supervisor/conf.d"
    fi

    log "Nginx 配置目录: $NGINX_CONF_DIR"
    log "Supervisor 配置目录: $SUPERVISOR_CONF_DIR"
}

install_deps() {
    log "安装基础依赖..."
    case $OS in
        alinux|centos|rhel|fedora|rocky|almalinux)
            dnf install -y python3.11 python3.11-pip nginx mysql-server supervisor gcc mariadb-connector-c-devel || true
            PYTHON_BIN="python3.11"
            ;;
        ubuntu|debian)
            apt-get update
            apt-get install -y python3.11 python3.11-venv python3-pip nginx mysql-server supervisor libmysqlclient-dev build-essential || true
            PYTHON_BIN="python3.11"
            ;;
        *)
            log "不支持的操作系统: $OS"
            exit 1
            ;;
    esac
}

setup_swap() {
    if ! swapon --show | grep -q swapfile; then
        log "创建 2G Swap..."
        fallocate -l 2G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=2048
        chmod 600 /swapfile
        mkswap /swapfile
        swapon /swapfile
        echo '/swapfile none swap sw 0 0' >> /etc/fstab
    fi
}

setup_mysql() {
    log "启动 MySQL..."
    systemctl start mysqld || systemctl start mysql || true
    systemctl enable mysqld || systemctl enable mysql || true

    # 读取 .env 中的数据库配置
    if [ -f "${PROJECT_DIR}/.env" ]; then
        DB_URL=$(grep DATABASE_URL "${PROJECT_DIR}/.env" | cut -d '=' -f2-)
    fi

    if [ -z "$DB_URL" ]; then
        log "未找到 DATABASE_URL，跳过自动建库"
        return
    fi

    # 解析数据库名
    DB_NAME=$(echo "$DB_URL" | sed -n 's/.*\/\([a-zA-Z0-9_]*\).*/\1/p')
    DB_USER=$(echo "$DB_URL" | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
    DB_PASS=$(echo "$DB_URL" | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')

    log "创建数据库: $DB_NAME"
    mysql -u root -e "CREATE DATABASE IF NOT EXISTS ${DB_NAME} DEFAULT CHARACTER SET utf8mb4;" 2>/dev/null || true
    if [ "$DB_USER" != "root" ]; then
        mysql -u root -e "CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';" 2>/dev/null || true
        mysql -u root -e "GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';" 2>/dev/null || true
        mysql -u root -e "FLUSH PRIVILEGES;" 2>/dev/null || true
    fi

    # 导入表结构
    if [ -f "${PROJECT_DIR}/database/schema.sql" ]; then
        log "导入数据库表结构..."
        mysql -u root "${DB_NAME}" < "${PROJECT_DIR}/database/schema.sql" || true
    fi
}

setup_python() {
    log "创建 Python 虚拟环境..."
    cd "$PROJECT_DIR"
    $PYTHON_BIN -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
}

build_frontend() {
    log "构建前端..."
    cd "${PROJECT_DIR}/frontend"
    npm install
    chmod +x node_modules/.bin/* 2>/dev/null || true
    npm run build
}

deploy_static() {
    log "部署静态文件..."
    mkdir -p "${WWW_DIR}/frontend"
    cp -r "${PROJECT_DIR}/frontend/dist" "${WWW_DIR}/frontend/"
    mkdir -p "${WWW_DIR}/static"
    cp -r "${PROJECT_DIR}/static" "${WWW_DIR}/"

    # 上传目录做软链接
    rm -rf "${WWW_DIR}/static/uploads"
    ln -s "${PROJECT_DIR}/static/uploads" "${WWW_DIR}/static/uploads"
}

setup_nginx() {
    log "配置 Nginx..."
    cp "${PROJECT_DIR}/deploy/nginx-http.conf" "${NGINX_CONF_DIR}/sh-ai.conf"

    # 屏蔽默认 server
    if [ -f /etc/nginx/nginx.conf ]; then
        sed -i 's/    listen       80 default_server;/#    listen       80 default_server;/g' /etc/nginx/nginx.conf || true
        sed -i 's/    listen       \[::\]:80 default_server;/#    listen       [::]:80 default_server;/g' /etc/nginx/nginx.conf || true
    fi

    nginx -t
    systemctl restart nginx || systemctl reload nginx
}

setup_supervisor() {
    log "配置 Supervisor..."
    sed -e "s|PROJECT_DIR|${PROJECT_DIR}|g" \
        -e "s|PYTHON_BIN|${PROJECT_DIR}/venv/bin/uvicorn|g" \
        "${PROJECT_DIR}/deploy/supervisor.ini" > "${SUPERVISOR_CONF_DIR}/sh-ai.ini"

    systemctl start supervisord || true
    systemctl enable supervisord || true
    supervisorctl reread
    supervisorctl update
    supervisorctl start sh-ai || supervisorctl restart sh-ai
}

main() {
    log "开始部署会场精灵..."

    if [ "$(id -u)" != "0" ]; then
        log "请使用 root 权限运行此脚本"
        exit 1
    fi

    detect_os
    detect_paths

    if [ ! -d "$PROJECT_DIR" ]; then
        log "项目目录不存在: $PROJECT_DIR"
        exit 1
    fi

    install_deps
    setup_swap
    setup_mysql
    setup_python
    build_frontend
    deploy_static
    setup_nginx
    setup_supervisor

    log "部署完成！"
    log "访问: http://$(curl -s ifconfig.me 2>/dev/null || echo '你的服务器IP')"
}

main "$@"
