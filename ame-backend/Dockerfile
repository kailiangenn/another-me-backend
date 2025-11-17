# Another Me Backend - Docker 镜像
# Python 3.11 + FastAPI + AME 引擎

FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制 AME 引擎
COPY ame/ /app/ame/

# 复制后端代码
COPY backend/ /app/backend/

# 安装 AME 引擎依赖
WORKDIR /app/ame
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -e .

# 安装后端依赖
WORKDIR /app/backend
RUN pip install --no-cache-dir -r requirements.txt

# 创建数据目录
RUN mkdir -p /app/data/faiss /app/data/falkor /app/data/metadata /app/data/uploads

# 暴露端口
EXPOSE 8000

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV DATA_DIR=/app/data

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
