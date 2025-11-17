"""
健康检查 API
"""
from fastapi import APIRouter
from app.models.responses import HealthResponse
from app.core.config import get_settings
from datetime import datetime

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    健康检查接口
    
    Returns:
        服务状态信息
    """
    settings = get_settings()
    
    return HealthResponse(
        status="ok",
        version=settings.APP_VERSION,
        timestamp=datetime.now()
    )
