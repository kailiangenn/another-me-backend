"""
配置管理模块
负责加载和管理应用配置
"""
import os
from pathlib import Path
from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基础配置
    APP_NAME: str = "Another Me API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # API 配置
    API_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # LLM 配置
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # 数据路径配置
    DATA_DIR: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent.parent / "data")
    RAG_VECTOR_STORE_PATH: Optional[Path] = None
    MEM_VECTOR_STORE_PATH: Optional[Path] = None
    UPLOADS_DIR: Optional[Path] = None
    CONFIG_DIR: Optional[Path] = None
    
    # 向量数据库配置
    VECTOR_STORE_TYPE: str = "memu"
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    
    # RAG 配置
    RAG_TOP_K: int = 5
    RAG_CHUNK_SIZE: int = 500
    RAG_CHUNK_OVERLAP: int = 50
    
    # MEM 配置
    MEM_TOP_K: int = 10
    MEM_SIMILARITY_THRESHOLD: float = 0.7
    
    # 文件上传配置
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".txt", ".pdf", ".doc", ".docx", ".md"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 初始化路径
        self._init_paths()
    
    def _init_paths(self):
        """初始化路径配置"""
        # 确保数据目录存在
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # 设置子目录路径
        if not self.RAG_VECTOR_STORE_PATH:
            self.RAG_VECTOR_STORE_PATH = self.DATA_DIR / "rag_vector_store"
            self.RAG_VECTOR_STORE_PATH.mkdir(parents=True, exist_ok=True)
        
        if not self.MEM_VECTOR_STORE_PATH:
            self.MEM_VECTOR_STORE_PATH = self.DATA_DIR / "mem_vector_store"
            self.MEM_VECTOR_STORE_PATH.mkdir(parents=True, exist_ok=True)
        
        if not self.UPLOADS_DIR:
            self.UPLOADS_DIR = self.DATA_DIR / "uploads"
            self.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        
        if not self.CONFIG_DIR:
            self.CONFIG_DIR = self.DATA_DIR / "config"
            self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    @property
    def is_configured(self) -> bool:
        """检查是否已配置 API Key"""
        return bool(self.OPENAI_API_KEY)


# 全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings


def reload_settings():
    """重新加载配置"""
    global settings
    settings = Settings()
    return settings
