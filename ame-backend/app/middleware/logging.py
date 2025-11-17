"""
日志中间件
记录所有 HTTP 请求
"""
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logger import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """HTTP 请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next):
        """
        处理请求并记录日志
        
        Args:
            request: HTTP 请求
            call_next: 下一个处理函数
            
        Returns:
            HTTP 响应
        """
        start_time = time.time()
        
        # 记录请求
        logger.info(f"Request: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录响应
            logger.info(
                f"Response: {request.method} {request.url.path} "
                f"Status={response.status_code} Time={process_time:.3f}s"
            )
            
            # 添加处理时间头
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # 记录异常
            process_time = time.time() - start_time
            logger.error(
                f"Error: {request.method} {request.url.path} "
                f"Time={process_time:.3f}s Error={str(e)}"
            )
            raise
