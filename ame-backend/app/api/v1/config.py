"""
配置管理 API
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.models.base_enums import TaskPriority, TaskStatus
from app.services.config_service import ConfigService, get_config_service
from app.models.requests import ConfigRequest, ConfigTestRequest
from app.models.responses import ApiResponse
from app.core.logger import get_logger
router = APIRouter()
logger = get_logger(__name__)


@router.post("/save", response_model=ApiResponse)
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

        return ApiResponse.success(data=result)

    except Exception as e:
        logger.error(f"Save config failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save configuration: {str(e)}"
        )


@router.get("/load", response_model=ApiResponse)
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

        return ApiResponse.success(data=config)

    except Exception as e:
        logger.error(f"Load config failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load configuration: {str(e)}"
        )


@router.post("/test", response_model=ApiResponse)
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
        return ApiResponse.success(data=result)

    except Exception as e:
        logger.error(f"Test config failed: {e}")
        return ApiResponse.error(code=500, msg=f"Test failed: {str(e)}")


@router.get("/dict", response_model=ApiResponse)
async def get_dict(
        type: str
):

    try:
        if type == 'task_priority':
            result = TaskPriority.choices()
        elif type == 'task_status':
            result = TaskStatus.choices()
        else:
            result = []
        return ApiResponse.success(data=result)

    except Exception as e:
        logger.error(f"Test config failed: {e}")
        return ApiResponse.error(code=500, msg=f"Test failed: {str(e)}")