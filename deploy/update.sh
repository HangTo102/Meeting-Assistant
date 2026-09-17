#!/bin/bash
set -e

# 会场精灵 - 代码更新脚本

PROJECT_DIR="/root/sh-ai"
WWW_DIR="/var/www/sh-ai"

cd "$PROJECT_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "更新后端依赖..."
source venv/bin/activate
pip install -r requirements.txt

log "清理缓存..."
find "$PROJECT_DIR" -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

log "重新构建前端..."
cd "${PROJECT_DIR}/frontend"
npm install
chmod +x node_modules/.bin/* 2>/dev/null || true
npm run build

log "同步静态文件..."
cp -r "${PROJECT_DIR}/frontend/dist" "${WWW_DIR}/frontend/"
cp -r "${PROJECT_DIR}/static" "${WWW_DIR}/"
rm -rf "${WWW_DIR}/static/uploads"
ln -s "${PROJECT_DIR}/static/uploads" "${WWW_DIR}/static/uploads"

log "重启后端..."
supervisorctl restart sh-ai

log "重新加载 Nginx..."
systemctl reload nginx || systemctl restart nginx

log "更新完成"
