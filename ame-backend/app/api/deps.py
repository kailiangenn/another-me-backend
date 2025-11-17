"""
依赖注入
"""
from typing import Generator
from app.services.rag_service import get_rag_service
from app.services.mem_service import get_mem_service
from app.services.config_service import get_config_service


# 服务依赖
def get_rag_service_dep():
    """获取 RAG 服务依赖"""
    return get_rag_service()


def get_mem_service_dep():
    """获取 MEM 服务依赖"""
    return get_mem_service()


def get_config_service_dep():
    """获取配置服务依赖"""
    return get_config_service()
