#!/bin/bash

# ============================================
# 会场精灵 - 一键启动脚本
# 使用前请先配置 .env 中的环境变量
# ============================================

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=========================================="
echo "  会场精灵 - 启动中..."
echo "=========================================="

# ----------------------
# 1. 后端环境准备
# ----------------------
echo ""
echo "[1/4] 配置 Python 虚拟环境..."

cd "$PROJECT_DIR"

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "  -> 虚拟环境已创建"
fi

source venv/bin/activate

# 安装依赖
pip install -r requirements.txt -q
echo "  -> Python 依赖安装完成"

# ----------------------
# 2. 初始化数据库（可选）
# ----------------------
echo ""
echo "[2/4] 检查数据库..."

if [ ! -z "$DATABASE_URL" ] || [ -f ".env" ]; then
    echo "  -> 检测到数据库配置，如需初始化请运行:"
    echo "     python database/init_db.py"
else
    echo "  -> 未检测到数据库配置，请确保 .env 文件已配置"
fi

# ----------------------
# 3. 构建并启动前端
# ----------------------
echo ""
echo "[3/4] 启动前端..."

cd "$PROJECT_DIR/frontend"

if [ ! -d "node_modules" ]; then
    echo "  -> 安装前端依赖..."
    npm install
fi

# 在后台启动前端开发服务器
npm run dev &
FRONTEND_PID=$!
echo "  -> 前端已启动 (PID: $FRONTEND_PID)"
echo "  -> 访问地址: http://localhost:5173"

# ----------------------
# 4. 启动后端
# ----------------------
echo ""
echo "[4/4] 启动后端..."

cd "$PROJECT_DIR"

echo "  -> FastAPI 服务启动中..."
echo "  -> API 文档: http://localhost:8000/api/docs"
echo ""

python main.py

# 进程退出时关闭前端
kill $FRONTEND_PID 2>/dev/null
