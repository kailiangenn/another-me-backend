"""
数据生命周期管理任务
实现热温冷数据自动降温策略
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
import asyncio

# 导入 ame 核心模块
from ame.repository.hybrid_repository import HybridRepository
from ame.models.domain import DataLayer, Document

from app.core.config import get_settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class LifecycleManager:
    """数据生命周期管理器"""
    
    def __init__(self):
        """初始化生命周期管理器"""
        settings = get_settings()
        
        # 配置参数
        self.hot_data_days = settings.HOT_DATA_DAYS if hasattr(settings, 'HOT_DATA_DAYS') else 7
        self.warm_data_days = settings.WARM_DATA_DAYS if hasattr(settings, 'WARM_DATA_DAYS') else 30
        self.importance_threshold = settings.IMPORTANCE_THRESHOLD if hasattr(settings, 'IMPORTANCE_THRESHOLD') else 0.7
        
        # 存储仓库（可以配置多个）
        self.repositories: Dict[str, HybridRepository] = {}
        
        logger.info(f"Lifecycle Manager initialized (HOT: {self.hot_data_days}d, WARM: {self.warm_data_days}d)")
    
    def register_repository(self, name: str, repository: HybridRepository):
        """
        注册存储仓库
        
        Args:
            name: 仓库名称
            repository: 仓库实例
        """
        self.repositories[name] = repository
        logger.info(f"Repository registered: {name}")
    
    async def run_lifecycle_task(self):
        """
        执行数据生命周期管理任务
        
        主要功能：
        1. 扫描所有文档
        2. 根据时间和重要性计算数据层级
        3. 执行数据降温（HOT -> WARM -> COLD）
        """
        logger.info("Starting lifecycle management task")
        
        try:
            total_processed = 0
            total_demoted = 0
            
            # 遍历所有注册的仓库
            for repo_name, repository in self.repositories.items():
                logger.info(f"Processing repository: {repo_name}")
                
                processed, demoted = await self._process_repository(repository)
                
                total_processed += processed
                total_demoted += demoted
                
                logger.info(f"Repository {repo_name} completed: {processed} processed, {demoted} demoted")
            
            logger.info(f"Lifecycle task completed: {total_processed} documents processed, {total_demoted} demoted")
            
            return {
                "success": True,
                "total_processed": total_processed,
                "total_demoted": total_demoted,
                "repositories": len(self.repositories)
            }
            
        except Exception as e:
            logger.error(f"Lifecycle task failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _process_repository(self, repository: HybridRepository) -> tuple:
        """
        处理单个仓库的生命周期
        
        Args:
            repository: 存储仓库
            
        Returns:
            (处理数量, 降温数量)
        """
        processed = 0
        demoted = 0
        
        # 调用仓库的生命周期管理方法
        result = await repository.lifecycle_management()
        
        processed = result.get("total_documents", 0)
        demoted = result.get("demoted", 0)
        
        return processed, demoted
    
    async def cleanup_old_data(self, days_threshold: int = 365):
        """
        清理过期数据
        
        Args:
            days_threshold: 保留天数阈值
        """
        logger.info(f"Starting old data cleanup (threshold: {days_threshold} days)")
        
        try:
            total_deleted = 0
            cutoff_date = datetime.now() - timedelta(days=days_threshold)
            
            for repo_name, repository in self.repositories.items():
                logger.info(f"Cleaning up repository: {repo_name}")
                # TODO: 实现基于时间的批量删除功能
                # deleted = await repository.delete_older_than(cutoff_date)
                # total_deleted += deleted
            
            logger.info(f"Cleanup completed: {total_deleted} documents deleted")
            
            return {
                "success": True,
                "deleted": total_deleted
            }
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# 全局实例
_lifecycle_manager: LifecycleManager = None


def get_lifecycle_manager() -> LifecycleManager:
    """获取生命周期管理器实例"""
    global _lifecycle_manager
    if _lifecycle_manager is None:
        _lifecycle_manager = LifecycleManager()
    return _lifecycle_manager


# 定时任务函数（供 APScheduler 调用）
async def run_lifecycle_task():
    """执行数据生命周期任务"""
    manager = get_lifecycle_manager()
    return await manager.run_lifecycle_task()


async def run_cleanup_task():
    """执行数据清理任务"""
    manager = get_lifecycle_manager()
    return await manager.cleanup_old_data()
