"""
MEM 对话服务
封装 AME MEM 模块的业务逻辑
"""
import sys
import os
from pathlib import Path
from typing import AsyncIterator, List, Dict, Any, Optional
from datetime import datetime

# 添加 AME 路径
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "ame"))

from ame.mem.mimic_engine import MimicEngine
from ame.llm_caller.caller import LLMCaller
from app.core.config import get_settings
from app.core.logger import get_logger
from app.core.exceptions import ConfigurationError, LLMError
from app.models.responses import Memory

logger = get_logger(__name__)


class MEMService:
    """MEM 对话服务"""
    
    def __init__(self):
        """初始化 MEM 服务"""
        settings = get_settings()
        
        # 检查配置
        if not settings.is_configured:
            logger.warning("API Key not configured")
            self.engine = None
            return
        
        try:
            # 初始化 LLM Caller
            llm_caller = LLMCaller(
                api_key=settings.API_KEY,
                base_url=settings.BASE_URL,
                model=settings.MODEL
            )
        except Exception as e:
            logger.error(f"Failed to initialize LLM caller: {e}")
            raise LLMError(
                message="Failed to initialize LLM service",
                detail=str(e)
            )
        
        try:
            # 初始化模仿引擎
            self.engine = MimicEngine(
                llm_caller=llm_caller,
                vector_store_type=settings.VECTOR_STORE_TYPE,
                db_path=str(settings.MEM_VECTOR_STORE_PATH)
            )
            
            logger.info("MEM Service initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize MEM service: {e}")
            self.engine = None
            raise
    
    def _check_engine(self):
        """检查引擎是否初始化"""
        if self.engine is None:
            raise ConfigurationError(
                message="MEM engine not initialized",
                detail="Please configure API key first"
            )
    
    async def chat_stream(
        self,
        message: str,
        temperature: float = 0.8
    ) -> AsyncIterator[str]:
        """
        流式对话
        
        Args:
            message: 用户消息
            temperature: 温度参数
            
        Yields:
            文本片段
        """
        self._check_engine()
        
        logger.info(f"Chat request: {message[:50]}...")
        
        try:
            async for chunk in self.engine.generate_response_stream(
                prompt=message,
                temperature=temperature,
                use_history=True
            ):
                yield chunk
                
        except Exception as e:
            logger.error(f"Chat error: {e}")
            raise
    
    async def chat(
        self,
        message: str,
        temperature: float = 0.8
    ) -> str:
        """
        非流式对话
        
        Args:
            message: 用户消息
            temperature: 温度参数
            
        Returns:
            AI 回复
        """
        self._check_engine()
        
        logger.info(f"Chat request: {message[:50]}...")
        
        try:
            response = await self.engine.generate_response(
                prompt=message,
                temperature=temperature,
                use_history=True
            )
            
            logger.info("Chat response generated")
            return response
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            raise
    
    async def learn_from_conversation(
        self,
        message: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        从对话中学习
        
        Args:
            message: 用户消息
            context: 对话上下文
            
        Returns:
            学习结果
        """
        self._check_engine()
        
        logger.info("Learning from conversation")
        
        try:
            await self.engine.learn_from_conversation(
                user_message=message,
                context=context
            )
            
            logger.info("Learning completed")
            
            return {
                "success": True,
                "message": "Conversation learned successfully"
            }
            
        except Exception as e:
            logger.error(f"Learning error: {e}")
            raise
    
    async def get_memories(
        self,
        limit: int = 100
    ) -> List[Memory]:
        """
        获取记忆列表
        
        Args:
            limit: 返回数量限制
            
        Returns:
            记忆列表
        """
        self._check_engine()
        
        logger.debug("Getting memories")
        
        try:
            # TODO: 实现获取记忆功能
            # 目前返回空列表
            logger.warning("Get memories not yet fully implemented")
            return []
            
        except Exception as e:
            logger.error(f"Failed to get memories: {e}")
            raise
    
    async def delete_memory(self, memory_id: str) -> bool:
        """
        删除记忆
        
        Args:
            memory_id: 记忆 ID
            
        Returns:
            是否成功
        """
        self._check_engine()
        
        logger.info(f"Deleting memory: {memory_id}")
        
        try:
            # TODO: 实现删除记忆功能
            logger.warning("Delete memory not yet implemented")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id}: {e}")
            raise


# 全局服务实例
_mem_service: Optional[MEMService] = None


def get_mem_service() -> MEMService:
    """获取 MEM 服务实例"""
    global _mem_service
    if _mem_service is None:
        _mem_service = MEMService()
    return _mem_service


def reload_mem_service():
    """重新加载 MEM 服务（配置更新后调用）"""
    global _mem_service
    _mem_service = None
    return get_mem_service()
