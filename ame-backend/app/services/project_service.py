import os
import random
from typing import Optional

from app.core.config import get_settings
from app.core.logger import get_logger
from app.core.exceptions import ConfigurationError, StorageError, LLMError, APIException

logger = get_logger(__name__)


class ProjectService:
    """工作场景服务"""

    def __init__(self):
        settings = get_settings()

        # 检查配置
        # if not settings.is_configured:
        #     raise ConfigurationError(
        #         message="Work service not configured",
        #         detail="Please configure OpenAI API Key first"
        #     )
        self.history_analysis_path = settings.PROJECT_ANALYSIS_PATH / settings.HISTORY_ANALYSIS_FILE_NAME
        self.project_analysis_path = settings.PROJECT_ANALYSIS_PATH / settings.PROJECT_ANALYSIS_FILE_NAME

    def analysis_project_desc(self, project_desc):
        """项目分析"""
        # todo chenchenaq 替换方法
        # 1. 调用ame方法获取分析结果
        try:
            analysis_result = "这里是一个虚拟的项目分析文案...." + str(random.random())
        except Exception as e:
            logger.warning(f"项目分析异常，project_desc:{project_desc},e:{str(e)}")
            raise APIException("项目分析异常：" + str(e))

        # 2. 如果当前项目分析文件存在，先删除之前的历史记录，再将其重命名为历史分析文件
        if self.project_analysis_path.exists():
            if self.history_analysis_path.exists():
                self.history_analysis_path.unlink()
            os.rename(self.project_analysis_path, self.history_analysis_path)

        # 3. 将新的分析结果写入项目分析文件
        self.project_analysis_path.parent.mkdir(parents=True, exist_ok=True)
        self.project_analysis_path.write_text(analysis_result, encoding="utf-8")

        return analysis_result

    def get_history_project_analysis(self):
        """获取历史项目分析结果"""
        # 读取历史分析文件:.txt
        try:
            if self.history_analysis_path.is_file():
                return self.history_analysis_path.read_text(encoding="utf-8")
            else:
                return ""
        except Exception as e:
            raise APIException(message="未正常读取历史分析结果文件，请检查。" + str(e))


# 全局服务实例
_project_service: Optional[ProjectService] = None


def get_project_service() -> ProjectService:
    """获取工作服务实例"""
    global _project_service
    if _project_service is None:
        _project_service = ProjectService()
    return _project_service
