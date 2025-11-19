from datetime import datetime
from enum import IntEnum
from typing import Optional, List, Dict

from pydantic import BaseModel

from app.core.config import get_settings
from app.core.logger import get_logger
from app.core.exceptions import ConfigurationError
from app.database.sqlite.schema import get_sqlite_db
from app.models.base_enums import TaskPriority, TaskStatus

logger = get_logger(__name__)


class SuggestService:
    """建议"""

    def __init__(self):
        settings = get_settings()
        self.file_path = settings.SUGGEST_STORE_PATH
        self.file_prefix = settings.SUGGEST_FILE_PREFIX

        # 检查配置
        # if not settings.is_configured:
        #     raise ConfigurationError(
        #         message="Work service not configured",
        #         detail="Please configure OpenAI API Key first"
        #     )

    async def get_suggest_by_date(self, date: datetime = None):
        """获取指定日期建议(默认为今日)"""
        if date is None:
            date = datetime.now().date()

        # 构造文件名：suggest_2025-11-19.txt
        filename = f"{self.file_prefix}_{date.isoformat()}.txt"
        file_full_path = self.file_path / filename

        if not file_full_path.exists():
            return ""

        try:
            with open(file_full_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            return content
        except Exception as e:
            raise e

    async def generate_and_save_suggest(self):
        """调用三方方法生成今日建议并写到指定文件里"""
        today = datetime.now().date()

        # 1. 构造文件路径
        filename = f"{self.file_prefix}_{today.isoformat()}.txt"
        file_full_path = self.file_path / filename

        # 2. 如果文件已存在，先删除
        if file_full_path.exists():
            try:
                file_full_path.unlink()  # 删除文件
            except Exception as e:
                logger.error(f"删除建议文件失败: {e}")

        # 3. 调用三方方法生成建议
        try:
            # todo chenchenaq 调用三方方法生成建议
            content = "这里是一段建议的md文案...."
        except Exception as e:
            logger.error(f"生成建议失败: {e}")
            raise e

        # 4. 写入新文件
        try:
            with open(file_full_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            logger.error(f"写入建议文件失败: {e}")
        return True


_suggest_service: Optional[SuggestService] = None


def get_suggest_service() -> SuggestService:
    """获取工作服务实例"""
    global _suggest_service
    if _suggest_service is None:
        _suggest_service = SuggestService()
    return _suggest_service
