"""
错误处理中间件
统一处理异常并返回标准错误响应
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logger import get_logger
from app.core.exceptions import APIException
from app.models.responses import ErrorResponse
from datetime import datetime
import traceback
import time

logger = get_logger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """全局错误处理中间件"""
    
    async def dispatch(self, request: Request, call_next):
        """
        处理请求并捕获异常
        
        Args:
            request: HTTP 请求
            call_next: 下一个处理函数
            
        Returns:
            HTTP 响应
        """
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # 记录请求时间
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except APIException as e:
            # 自定义 API 异常
            logger.warning(f"{e.__class__.__name__} on {request.url.path}: {e.message}")
            error_response = ErrorResponse(
                error=e.message,
                detail=e.detail,
                timestamp=datetime.now()
            )
            return JSONResponse(
                status_code=e.status_code,
                content=error_response.model_dump()
            )
            
        except ValueError as e:
            # 参数错误
            logger.warning(f"ValueError on {request.url.path}: {str(e)}")
            error_response = ErrorResponse(
                error="Invalid parameter",
                detail=str(e),
                timestamp=datetime.now()
            )
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=error_response.model_dump()
            )
            
        except FileNotFoundError as e:
            # 文件未找到
            logger.error(f"FileNotFoundError on {request.url.path}: {str(e)}")
            error_response = ErrorResponse(
                error="Resource not found",
                detail=str(e),
                timestamp=datetime.now()
            )
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=error_response.model_dump()
            )
            
        except PermissionError as e:
            # 权限错误
            logger.error(f"PermissionError on {request.url.path}: {str(e)}")
            error_response = ErrorResponse(
                error="Permission denied",
                detail=str(e),
                timestamp=datetime.now()
            )
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content=error_response.model_dump()
            )
        
        except TimeoutError as e:
            # 超时错误
            logger.error(f"TimeoutError on {request.url.path}: {str(e)}")
            error_response = ErrorResponse(
                error="Request timeout",
                detail="The request took too long to process",
                timestamp=datetime.now()
            )
            return JSONResponse(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                content=error_response.model_dump()
            )
            
        except Exception as e:
            # 其他未知错误
            logger.critical(
                f"Unhandled exception on {request.url.path}: {str(e)}\n{traceback.format_exc()}"
            )
            
            # 生产环境不暴露详细错误
            is_debug = getattr(request.app.state.settings, 'DEBUG', False)
            detail = str(e) if is_debug else "An internal error occurred"
            
            error_response = ErrorResponse(
                error="Internal server error",
                detail=detail,
                timestamp=datetime.now()
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=error_response.model_dump()
            )
