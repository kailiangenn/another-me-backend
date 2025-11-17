# Another Me Backend API 服务文档

## 概述

Another Me Backend 是基于 FastAPI 构建的 RESTful API 服务，为前端应用提供数据接口和业务逻辑处理。

**版本**: v0.1.0  
**框架**: FastAPI 0.109+  
**Python**: 3.11+

---

## 架构设计

### 目录结构

```
backend/
├── app/
│   ├── api/              # API 路由层
│   │   ├── v1/          # v1 版本 API
│   │   │   ├── health.py    # 健康检查
│   │   │   ├── rag.py       # RAG 知识库 API
│   │   │   ├── mem.py       # 记忆模仿 API
│   │   │   ├── config.py    # 配置管理 API
│   │   │   ├── work.py      # 工作场景 API (v0.1.0)
│   │   │   └── life.py      # 生活场景 API (v0.1.0)
│   │   └── deps.py      # 依赖注入
│   ├── core/            # 核心模块
│   │   ├── config.py    # 配置管理
│   │   └── logger.py    # 日志系统
│   ├── middleware/      # 中间件
│   │   ├── logging.py   # 日志中间件
│   │   ├── error_handler.py  # 错误处理
│   │   └── cors.py      # CORS 配置
│   ├── models/          # 数据模型
│   │   ├── requests.py  # 请求模型
│   │   └── responses.py # 响应模型
│   ├── services/        # 业务逻辑层
│   │   ├── rag_service.py      # RAG 服务
│   │   ├── mem_service.py      # MEM 服务
│   │   ├── config_service.py   # 配置服务
│   │   ├── work_service.py     # 工作场景服务 (v0.1.0)
│   │   └── life_service.py     # 生活场景服务 (v0.1.0)
│   ├── tasks/           # 定时任务 (v0.1.0)
│   │   ├── lifecycle.py   # 数据生命周期管理
│   │   └── scheduler.py   # 任务调度器
│   └── main.py          # 应用入口
├── requirements.txt     # Python 依赖
├── Dockerfile          # Docker 配置 (v0.1.0)
└── run.sh             # 启动脚本
```

### v0.1.0 新增功能

1. **双存储架构集成**
   - 服务层直接使用 `ame.repository.HybridRepository`
   - 统一的数据模型 `ame.models.domain.Document`
   - 支持 Faiss + Falkor + SQLite 混合存储

2. **场景化服务**
   - `WorkService`: 工作场景（周报生成、待办整理、会议总结）
   - `LifeService`: 生活场景（心情分析、兴趣追踪、生活建议）

3. **数据生命周期管理**
   - 自动数据降温（HOT → WARM → COLD）
   - 定时任务调度（APScheduler）
   - 过期数据清理

---

## API 端点

### 健康检查

```
GET /api/v1/health
```

**响应示例**:
```json
{
  "status": "ok",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

---

### RAG 知识库 API

#### 上传文档
```
POST /api/v1/rag/upload
Content-Type: multipart/form-data

file: <文件>
```

#### 检索知识
```
POST /api/v1/rag/search
Content-Type: application/json

{
  "query": "检索内容",
  "top_k": 5
}
```

#### 添加文本
```
POST /api/v1/rag/add-text
Content-Type: application/json

{
  "text": "知识内容",
  "source": "user_input"
}
```

---

### MEM 记忆模仿 API

#### 流式对话
```
POST /api/v1/mem/chat/stream
Content-Type: application/json

{
  "message": "用户消息",
  "temperature": 0.8
}
```

**响应**: Server-Sent Events (SSE) 流

#### 学习对话
```
POST /api/v1/mem/learn
Content-Type: application/json

{
  "message": "用户消息",
  "context": "对话上下文"
}
```

---

### 工作场景 API (v0.1.0)

#### 生成周报
```
POST /api/v1/work/weekly-report
Content-Type: application/json

{
  "start_date": "2024-01-01",
  "end_date": "2024-01-07"
}
```

#### 整理待办
```
POST /api/v1/work/organize-todos
Content-Type: application/json

{
  "todos": ["任务1", "任务2", "任务3"]
}
```

#### 总结会议
```
POST /api/v1/work/summarize-meeting
Content-Type: application/json

{
  "meeting_notes": "会议记录内容",
  "meeting_info": {
    "title": "会议标题",
    "time": "2024-01-01T10:00:00",
    "participants": ["张三", "李四"]
  }
}
```

---

### 生活场景 API (v0.1.0)

#### 分析心情
```
POST /api/v1/life/analyze-mood
Content-Type: application/json

{
  "mood_entry": "今天心情很好...",
  "entry_time": "2024-01-01T20:00:00"
}
```

#### 追踪兴趣
```
GET /api/v1/life/track-interests?period_days=30
```

#### 生成生活总结
```
POST /api/v1/life/life-summary
Content-Type: application/json

{
  "period": "week"  // week | month | year
}
```

---

## 环境配置

### 必需环境变量

```bash
# OpenAI API 配置
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo

# 数据存储路径
DATA_DIR=./data

# 数据生命周期配置 (v0.1.0)
HOT_DATA_DAYS=7
WARM_DATA_DAYS=30
IMPORTANCE_THRESHOLD=0.7
```

### 配置文件

在项目根目录创建 `.env` 文件，参考 `.env.example`。

---

## 本地开发

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 安装 AME 引擎

```bash
cd ../ame
pip install -e .
```

### 3. 启动服务

```bash
cd ../backend
./run.sh
```

或使用 uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Docker 部署

### 构建镜像

```bash
cd /path/to/another-me
docker build -f backend/Dockerfile -t another-me-backend .
```

### 运行容器

```bash
docker run -d \
  --name another-me-backend \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e OPENAI_API_KEY=your-key \
  another-me-backend
```

### 使用 Docker Compose

```bash
cd deployment
docker-compose up -d
```

---

## 定时任务管理 (v0.1.0)

### 配置的定时任务

1. **数据生命周期管理** - 每天凌晨 2:00
   - 扫描所有文档
   - 根据时间和重要性执行数据降温
   - HOT → WARM → COLD

2. **过期数据清理** - 每周日凌晨 3:00
   - 删除超过 365 天的低价值数据
   - 释放存储空间

### 手动触发任务

```python
from app.tasks.scheduler import get_scheduler

scheduler = get_scheduler()
await scheduler.run_job_now("lifecycle_management")
```

---

## 错误处理

所有 API 错误返回统一格式：

```json
{
  "detail": "错误描述",
  "error_type": "错误类型",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

常见错误码：
- `400`: 请求参数错误
- `401`: 未授权（API Key 未配置）
- `404`: 资源不存在
- `500`: 服务器内部错误

---

## 日志系统

日志输出到控制台，支持彩色输出（开发环境）。

日志级别：
- `DEBUG`: 详细调试信息
- `INFO`: 一般信息
- `WARNING`: 警告信息
- `ERROR`: 错误信息

---

## 性能优化

1. **异步处理**: 所有 I/O 操作使用 async/await
2. **流式响应**: 大文本生成使用 SSE 流式输出
3. **缓存机制**: LLM 调用结果可缓存（可选）
4. **连接池**: 数据库连接复用

---

## 测试

### 运行单元测试

```bash
pytest backend/tests/
```

### 测试覆盖率

```bash
pytest --cov=app backend/tests/
```

---

## 贡献指南

1. 新增 API 端点需在 `app/api/v1/` 下创建路由文件
2. 业务逻辑封装在 `app/services/` 中
3. 数据模型定义在 `app/models/` 中
4. 使用 Pydantic 进行请求/响应验证
5. 添加适当的日志记录
6. 编写单元测试

---

## 常见问题

### Q: 如何更改 API 端口？

A: 修改 `run.sh` 或使用环境变量 `PORT=8080 uvicorn app.main:app`

### Q: 如何禁用定时任务？

A: 在 `app/main.py` 中注释掉 `start_scheduler()` 调用

### Q: 如何增加新的定时任务？

A: 在 `app/tasks/scheduler.py` 的 `setup_tasks()` 方法中添加新任务

---

## 更新日志

### v0.1.0 (2024-01-01)

**新增功能**:
- ✅ 双存储架构集成（Faiss + Falkor + SQLite）
- ✅ 工作场景服务（周报、待办、会议）
- ✅ 生活场景服务（心情、兴趣、总结）
- ✅ 数据生命周期管理
- ✅ 定时任务调度器
- ✅ Docker 容器化支持

**改进**:
- 🔧 统一数据模型
- 🔧 混合检索融合
- 🔧 sys.path 配置优化

---

## 相关文档

- [AME 引擎文档](../ame/README.md)
- [系统设计文档](../SYSTEM_DESIGN.md)
- [快速开始指南](../QUICK_START_REFACTOR.md)
- [实施清单](../IMPLEMENTATION_CHECKLIST.md)

---

## 技术支持

如有问题，请查看：
- API 文档: http://localhost:8000/docs
- 日志输出: 控制台
- 错误追踪: 检查日志中的 ERROR 级别消息
