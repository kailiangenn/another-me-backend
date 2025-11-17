#!/bin/bash
# Backend Server Startup Script

# 检查是否在 backend 目录
if [ ! -f "app/main.py" ]; then
    echo "Error: Please run this script from the backend directory"
    exit 1
fi

# 激活虚拟环境（如果存在）
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# 安装依赖
echo "Installing dependencies..."
pip install -r requirements.txt

# 启动服务器
echo "Starting Another Me Backend..."
cd app
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
