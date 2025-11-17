"""
配置服务
管理系统配置的保存和测试
"""
import json
from pathlib import Path
from typing import Dict, Any
from app.core.config import get_settings, reload_settings
from app.core.logger import get_logger
from app.services.mem_service import reload_mem_service

logger = get_logger(__name__)


class ConfigService:
    """配置管理服务"""
    
    def __init__(self):
        """初始化配置服务"""
        settings = get_settings()
        self.config_file = settings.CONFIG_DIR / "config.json"
        logger.info("Config Service initialized")
    
    async def save_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        保存配置
        
        Args:
            config: 配置字典
            
        Returns:
            保存结果
        """
        logger.info("Saving configuration")
        
        try:
            # 保存到配置文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            # 更新环境变量（临时）
            import os
            if 'api_key' in config:
                os.environ['OPENAI_API_KEY'] = config['api_key']
            if 'base_url' in config:
                os.environ['OPENAI_BASE_URL'] = config['base_url']
            if 'model' in config:
                os.environ['OPENAI_MODEL'] = config['model']
            
            # 重新加载配置
            reload_settings()
            
            # 重新初始化 MEM 服务
            try:
                reload_mem_service()
                logger.info("MEM service reloaded with new config")
            except Exception as e:
                logger.warning(f"Failed to reload MEM service: {e}")
            
            logger.info("Configuration saved successfully")
            
            return {
                "success": True,
                "message": "Configuration saved successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            raise
    
    async def load_config(self) -> Dict[str, Any]:
        """
        加载配置
        
        Returns:
            配置字典
        """
        logger.debug("Loading configuration")
        
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    logger.debug("Configuration loaded from file")
                    return config
            else:
                logger.debug("No configuration file found")
                return {}
                
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
    
    async def test_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        测试配置
        
        Args:
            config: 配置字典
            
        Returns:
            测试结果
        """
        logger.info("Testing configuration")
        
        result = {
            "success": True,
            "message": "Configuration is valid",
            "model_available": False,
            "embedding_available": False,
            "embedding_dimension": None
        }
        
        # 测试 LLM 模型
        try:
            from ame.llm_caller.caller import LLMCaller
            
            # 创建测试 LLM Caller
            llm_caller = LLMCaller(
                api_key=config.get('api_key', ''),
                base_url=config.get('base_url', 'https://api.openai.com/v1'),
                model=config.get('model', 'gpt-3.5-turbo')
            )
            
            # 测试调用
            messages = [
                {"role": "user", "content": "Say 'OK' if you receive this."}
            ]
            
            response = await llm_caller.generate(messages=messages)
            result["model_available"] = True
            logger.info("LLM model test successful")
            
        except Exception as e:
            logger.error(f"LLM model test failed: {e}")
            result["success"] = False
            result["message"] = f"LLM model test failed: {str(e)}"
            return result
        
        # 测试 Embedding 模型（如果配置了）
        embedding_model = config.get('embedding_model')
        embedding_dimension = config.get('embedding_dimension')
        
        if embedding_model and embedding_dimension:
            try:
                import openai
                
                # 创建 OpenAI 客户端
                client = openai.OpenAI(
                    api_key=config.get('api_key', ''),
                    base_url=config.get('base_url', 'https://api.openai.com/v1')
                )
                
                # 测试 Embedding 调用
                response = client.embeddings.create(
                    model=embedding_model,
                    input="test embedding",
                    encoding_format="float"
                )
                
                # 检查返回的向量维度
                actual_dimension = len(response.data[0].embedding)
                result["embedding_available"] = True
                result["embedding_dimension"] = actual_dimension
                
                # 检查维度是否匹配
                if actual_dimension != embedding_dimension:
                    logger.warning(
                        f"Embedding dimension mismatch: expected {embedding_dimension}, got {actual_dimension}"
                    )
                    result["message"] = (
                        f"✓ LLM model available\n"
                        f"✓ Embedding model available\n"
                        f"⚠ Warning: Configured dimension ({embedding_dimension}) "
                        f"differs from actual ({actual_dimension})"
                    )
                else:
                    result["message"] = (
                        f"✓ LLM model available\n"
                        f"✓ Embedding model available\n"
                        f"✓ Embedding dimension correct ({actual_dimension})"
                    )
                
                logger.info(f"Embedding test successful: {embedding_model}, dimension={actual_dimension}")
                
            except Exception as e:
                logger.error(f"Embedding test failed: {e}")
                result["embedding_available"] = False
                result["message"] = (
                    f"✓ LLM model available\n"
                    f"✗ Embedding test failed: {str(e)}"
                )
                # Embedding 测试失败不影响整体成功
        else:
            # 没有配置 Embedding，只测试了 LLM
            result["message"] = "✓ LLM model available (Embedding not configured)"
        
        logger.info("Configuration test completed")
        return result


# 全局服务实例
_config_service = None


def get_config_service() -> ConfigService:
    """获取配置服务实例"""
    global _config_service
    if _config_service is None:
        _config_service = ConfigService()
    return _config_service
