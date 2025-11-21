"""
配置管理模块
负责加载和管理应用配置
"""
import json
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

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
    PROJECT_STORE_PATH: Optional[Path] = None
    SUGGEST_STORE_PATH: Optional[Path] = None
    UPLOADS_DIR: Optional[Path] = None
    CONFIG_DIR: Optional[Path] = None

    # 向量数据库配置
    VECTOR_STORE_TYPE: str = "memu"
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    EMBEDDING_DIMENSION: Optional[int] = None

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

    # 项目分析配置
    PROJECT_ANALYSIS_FILE_NAME: str = "project_analysis.txt"
    HISTORY_ANALYSIS_FILE_NAME: str = "history_project_analysis.txt"

    # 建议配置
    SUGGEST_FILE_PREFIX: str = "suggest_"

    # falkor 配置
    FALKOR_HOST: str = "localhost"
    FALKOR_PORT: str = "6379"
    FALKOR_GRAPH_NAME: str = "ame_graph"
    FALKOR_PASSWORD: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 初始化路径
        self._init_paths()
        # 初始化配置
        self._init_config()

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

        if not self.PROJECT_STORE_PATH:
            self.PROJECT_STORE_PATH = self.DATA_DIR / "project_store"
            self.PROJECT_STORE_PATH.mkdir(parents=True, exist_ok=True)

        if not self.SUGGEST_STORE_PATH:
            self.SUGGEST_STORE_PATH = self.DATA_DIR / "suggest_store"
            self.SUGGEST_STORE_PATH.mkdir(parents=True, exist_ok=True)

        if not self.UPLOADS_DIR:
            self.UPLOADS_DIR = self.DATA_DIR / "uploads"
            self.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

        if not self.CONFIG_DIR:
            self.CONFIG_DIR = self.DATA_DIR / "config"
            self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    def _init_config(self):
        """初始化配置"""
        # 如果配置文件存在，读取配置文件
        config_file = self.CONFIG_DIR / "config.json"
        if config_file.exists():
            with open(config_file, "r") as f:
                config = json.load(f)
                self.OPENAI_API_KEY = config.get("api_key")
                self.OPENAI_BASE_URL = config.get("base_url")
                self.OPENAI_MODEL = config.get("model")
                self.EMBEDDING_MODEL = config.get("embedding_model")
                self.EMBEDDING_DIMENSION = config.get("embedding_dimension")
                self.FALKOR_PORT = config.get("falkor_port")
        else:
            # 如果不存在，创建默认配置文件
            default_config = {
                "api_key": self.OPENAI_API_KEY,
                "base_url": self.OPENAI_BASE_URL,
                "model": self.OPENAI_MODEL,
                "embedding_model": self.EMBEDDING_MODEL,
                "embedding_dimension": self.EMBEDDING_DIMENSION,
                "falkor_port": self.FALKOR_PORT,
                "falkor_graph_name": self.FALKOR_GRAPH_NAME,
                "falkor_password": self.FALKOR_PASSWORD
            }
            # 写入默认配置
            try:
                with open(config_file, "w", encoding="utf-8") as f:
                    json.dump(default_config, f, ensure_ascii=False, indent=4)
            except Exception as e:
                raise e

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
