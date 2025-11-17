"""
Another Me API - FastAPI 主应用
v0.1.0 - 集成新的双存储架构
"""
import sys
from pathlib import Path

# v0.1.0: 配置 sys.path 以导入 ame 核心模块
AME_ROOT = Path(__file__).parent.parent.parent / "ame"
if str(AME_ROOT) not in sys.path:
    sys.path.insert(0, str(AME_ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.v1 import health, rag, mem, config, work, life
from app.middleware.logging import LoggingMiddleware
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.core.config import get_settings
from app.core.logger import setup_logging, get_logger


# 初始化日志
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("Starting Another Me API...")
    settings = get_settings()
    logger.info(f"Version: {settings.APP_VERSION}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    logger.info(f"Data Directory: {settings.DATA_DIR}")
    
    yield
    
    # 关闭时
    logger.info("Shutting down Another Me API...")


# 创建 FastAPI 应用
app = FastAPI(
    title="Another Me API",
    version="1.0.0",
    description="AI 数字分身系统 API - 基于 RAG 和记忆模仿技术",
    lifespan=lifespan
)


# 配置 CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 添加自定义中间件
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorHandlerMiddleware)


# 存储设置到应用状态
app.state.settings = settings


# 注册路由
app.include_router(
    health.router,
    prefix="/api/v1",
    tags=["health"]
)

app.include_router(
    rag.router,
    prefix="/api/v1/rag",
    tags=["rag"]
)

app.include_router(
    mem.router,
    prefix="/api/v1/mem",
    tags=["mem"]
)

app.include_router(
    config.router,
    prefix="/api/v1/config",
    tags=["config"]
)

# v0.1.0 新增：工作和生活场景 API
app.include_router(
    work.router,
    prefix="/api/v1/work",
    tags=["work"]
)

app.include_router(
    life.router,
    prefix="/api/v1/life",
    tags=["life"]
)


# 根路径
@app.get("/")
async def root():
    """API 根路径"""
    return {
        "name": "Another Me API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
