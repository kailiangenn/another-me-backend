"""
自定义异常类
定义业务异常类型
"""
from fastapi import HTTPException, status


class APIException(Exception):
    """API 基础异常类"""
    
    def __init__(self, message: str, status_code: int = 500, detail: str = None):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)


class ConfigurationError(APIException):
    """配置错误（API Key 未配置等）"""
    
    def __init__(self, message: str = "Configuration error", detail: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail or "API Key not configured or invalid configuration"
        )


class StorageError(APIException):
    """存储错误（向量库、图谱库等）"""
    
    def __init__(self, message: str = "Storage error", detail: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail or "Failed to access storage system"
        )


class LLMError(APIException):
    """LLM 调用错误"""
    
    def __init__(self, message: str = "LLM error", detail: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail or "Failed to call LLM service"
        )


class ValidationError(APIException):
    """数据验证错误"""
    
    def __init__(self, message: str = "Validation error", detail: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail or "Invalid input data"
        )


class ResourceNotFoundError(APIException):
    """资源未找到错误"""
    
    def __init__(self, message: str = "Resource not found", detail: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail or "The requested resource was not found"
        )
