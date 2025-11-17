"""
配置管理 API
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.services.config_service import ConfigService, get_config_service
from app.models.requests import ConfigRequest, ConfigTestRequest
from app.models.responses import BaseResponse, ConfigTestResult
from app.core.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/save", response_model=BaseResponse)
async def save_config(
    request: ConfigRequest,
    service: ConfigService = Depends(get_config_service)
):
    """
    保存配置
    
    Args:
        request: 配置请求
        service: 配置服务实例
        
    Returns:
        保存结果
    """
    try:
        config_dict = request.model_dump()
        result = await service.save_config(config_dict)
        
        return BaseResponse(**result)
        
    except Exception as e:
        logger.error(f"Save config failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save configuration: {str(e)}"
        )


@router.get("/load")
async def load_config(
    service: ConfigService = Depends(get_config_service)
):
    """
    加载配置
    
    Args:
        service: 配置服务实例
        
    Returns:
        配置数据
    """
    try:
        config = await service.load_config()
        
        # 隐藏敏感信息
        if 'api_key' in config and config['api_key']:
            config['api_key'] = config['api_key'][:8] + '...'
        
        return config
        
    except Exception as e:
        logger.error(f"Load config failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load configuration: {str(e)}"
        )


@router.post("/test", response_model=ConfigTestResult)
async def test_config(
    request: ConfigTestRequest,
    service: ConfigService = Depends(get_config_service)
):
    """
    测试配置
    
    Args:
        request: 测试请求
        service: 配置服务实例
        
    Returns:
        测试结果
    """
    try:
        config_dict = request.model_dump()
        result = await service.test_config(config_dict)
        
        return ConfigTestResult(**result)
        
    except Exception as e:
        logger.error(f"Test config failed: {e}")
        return ConfigTestResult(
            success=False,
            message=f"Test failed: {str(e)}",
            model_available=False
        )
