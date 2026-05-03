#!/bin/bash

# 激活 Python 环境
source ~/anaconda3/bin/activate base  # 或你的 conda 环境名

# 切换到项目目录
cd /path/to/SH-AIv2

# 启动后端
echo "🚀 Starting FastAPI backend..."
python main.py
