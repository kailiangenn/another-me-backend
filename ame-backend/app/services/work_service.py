"""
工作场景服务
提供工作相关的AI辅助功能：周报生成、待办整理、会议总结等
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import sys
from pathlib import Path

# 导入 ame 核心模块
from ame.repository.hybrid_repository import HybridRepository
from ame.models.domain import Document, DocumentType, MemoryRetentionType
from ame.engines.work_engine import WorkEngine
from ame.mem.analyze_engine import AnalyzeEngine
from ame.mem.mimic_engine import MimicEngine
from ame.llm_caller.caller import LLMCaller

from app.core.config import get_settings
from app.core.logger import get_logger
from app.core.exceptions import ConfigurationError, StorageError, LLMError

logger = get_logger(__name__)


class WorkService:
    """工作场景服务"""
    
    def __init__(self):
        """初始化工作服务"""
        settings = get_settings()
        
        # 检查配置
        if not settings.is_configured:
            raise ConfigurationError(
                message="Work service not configured",
                detail="Please configure OpenAI API Key first"
            )
        
        try:
            # 初始化 LLM Caller
            self.llm_caller = LLMCaller(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL,
                model=settings.OPENAI_MODEL
            )
        except Exception as e:
            logger.error(f"Failed to initialize LLM caller: {e}")
            raise LLMError(
                message="Failed to initialize LLM service",
                detail=str(e)
            )
        
        try:
            # 初始化混合存储仓库
            self.repository = HybridRepository(
                faiss_index_path=str(settings.DATA_DIR / "faiss" / "work.index"),
                metadata_db_path=str(settings.DATA_DIR / "metadata" / "work.db"),
                graph_db_path=str(settings.DATA_DIR / "falkor" / "work.db")
            )
        except Exception as e:
            logger.error(f"Failed to initialize repository: {e}")
            raise StorageError(
                message="Failed to initialize storage",
                detail=str(e)
            )
        
        # 初始化分析引擎
        self.analyzer = AnalyzeEngine(
            repository=self.repository,
            llm_caller=self.llm_caller
        )
        
        # 初始化工作引擎
        self.work_engine = WorkEngine(
            repository=self.repository,
            llm_caller=self.llm_caller,
            analyze_engine=self.analyzer
        )
        
        logger.info("Work Service initialized")
    
    async def generate_weekly_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        生成工作周报
        
        Args:
            start_date: 开始日期（默认上周一）
            end_date: 结束日期（默认上周日）
            
        Returns:
            周报内容
        """
        logger.info("Generating weekly report")
        
        try:
            # 计算日期范围
            if end_date is None:
                end_date = datetime.now()
            if start_date is None:
                start_date = end_date - timedelta(days=7)
            
            # 使用 WorkEngine 生成周报
            report_obj = await self.work_engine.generate_weekly_report(
                user_id="default",
                start_date=start_date,
                end_date=end_date,
                style="professional"
            )
            
            logger.info("Weekly report generated successfully")
            
            return {
                "success": True,
                "report": report_obj.content,
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "key_tasks": [t.dict() for t in report_obj.key_tasks],
                "achievements": [a.dict() for a in report_obj.achievements],
                "statistics": report_obj.statistics
            }
            
        except Exception as e:
            logger.error(f"Failed to generate weekly report: {e}")
            raise
    
    async def generate_daily_report(
        self,
        date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        生成工作日报
        
        Args:
            date: 日期（默认今天）
            
        Returns:
            日报内容
        """
        logger.info("Generating daily report")
        
        try:
            # 计算日期范围
            if date is None:
                date = datetime.now()
            
            # 使用 WorkEngine 生成日报
            report_obj = await self.work_engine.generate_daily_report(
                user_id="default",
                date=date,
                style="professional"
            )
            
            logger.info("Daily report generated successfully")
            
            return {
                "success": True,
                "report": report_obj.content,
                "date": date.isoformat(),
                "tasks_completed": [t.dict() for t in report_obj.tasks_completed],
                "tasks_ongoing": [t.dict() for t in report_obj.tasks_ongoing],
                "highlights": report_obj.highlights
            }
            
        except Exception as e:
            logger.error(f"Failed to generate daily report: {e}")
            raise
    
    async def organize_todos(
        self,
        raw_todos: List[str]
    ) -> Dict[str, Any]:
        """
        智能整理待办事项
        
        Args:
            raw_todos: 原始待办列表
            
        Returns:
            整理后的待办事项
        """
        logger.info(f"Organizing {len(raw_todos)} todos")
        
        try:
            # 使用 WorkEngine 整理待办
            organized = await self.work_engine.organize_todos(
                raw_todos=raw_todos,
                context={}
            )
            
            logger.info("Todos organized successfully")
            
            return {
                "success": True,
                "organized_todos": {
                    "high": [t.dict() for t in organized.high_priority],
                    "medium": [t.dict() for t in organized.medium_priority],
                    "low": [t.dict() for t in organized.low_priority],
                    "formatted_text": organized.formatted_text
                },
                "original_count": organized.original_count,
                "organized_count": organized.organized_count
            }
            
        except Exception as e:
            logger.error(f"Failed to organize todos: {e}")
            raise
    
    async def summarize_meeting(
        self,
        meeting_notes: str,
        meeting_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        总结会议内容
        
        Args:
            meeting_notes: 会议记录
            meeting_info: 会议信息（标题、时间、参与者等）
            
        Returns:
            会议总结
        """
        logger.info("Summarizing meeting")
        
        try:
            # 构建提示词
            prompt = self._build_meeting_summary_prompt(meeting_notes, meeting_info)
            
            # 调用 LLM 总结
            response = await self.llm_caller.call(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            
            # 存储会议记录
            doc = Document(
                id=f"meeting_{datetime.now().timestamp()}",
                content=meeting_notes,
                doc_type=DocumentType.WORK_LOG,
                source="meeting",
                timestamp=datetime.now(),
                retention_type=MemoryRetentionType.PERMANENT,
                metadata=meeting_info or {}
            )
            
            await self.repository.create(doc)
            
            logger.info("Meeting summarized and stored")
            
            return {
                "success": True,
                "summary": response,
                "document_id": doc.id
            }
            
        except Exception as e:
            logger.error(f"Failed to summarize meeting: {e}")
            raise
    
    async def track_project_progress(
        self,
        project_name: str
    ) -> Dict[str, Any]:
        """
        追踪项目进度
        
        Args:
            project_name: 项目名称
            
        Returns:
            项目进度分析
        """
        logger.info(f"Tracking progress for project: {project_name}")
        
        try:
            # 使用 WorkEngine 追踪项目进度
            progress = await self.work_engine.track_project_progress(
                project_name=project_name,
                user_id="default"
            )
            
            logger.info("Project progress tracked successfully")
            
            return {
                "success": True,
                "project_name": progress.project_name,
                "completion_rate": progress.completion_rate,
                "status": progress.status,
                "timeline": progress.timeline,
                "risks": progress.risks,
                "report": progress.report
            }
            
        except Exception as e:
            logger.error(f"Failed to track project progress: {e}")
            raise
    
    # ==================== 辅助方法 ====================
    
    async def _get_work_logs(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Document]:
        """
        获取指定时间范围内的工作记录
        
        使用 HybridRepository 的时间范围检索功能
        """
        # 使用时间范围检索
        docs = await self.repository.search_by_time_range(
            start_date=start_date,
            end_date=end_date,
            doc_type=DocumentType.WORK_LOG,
            limit=100
        )
        
        return docs
    
    def _build_todo_prompt(self, raw_todos: List[str]) -> str:
        """构建待办整理提示词"""
        todos_text = "\n".join([f"- {todo}" for todo in raw_todos])
        
        return f"""请帮我整理以下待办事项，按照优先级和类别进行分组：

{todos_text}

请按照以下格式输出：

**高优先级**
- [任务1]
- [任务2]

**中优先级**
- [任务3]

**低优先级**
- [任务4]

同时，如果发现有重复或相似的任务，请合并它们。"""
    
    def _build_meeting_summary_prompt(
        self,
        notes: str,
        info: Optional[Dict[str, Any]]
    ) -> str:
        """构建会议总结提示词"""
        info_text = ""
        if info:
            info_text = f"""
会议标题：{info.get('title', '未知')}
会议时间：{info.get('time', '未知')}
参与者：{', '.join(info.get('participants', []))}
"""
        
        return f"""请总结以下会议内容：

{info_text}

会议记录：
{notes}

请按照以下格式输出：

**会议概要**
[简短描述会议主题和目的]

**关键讨论点**
1. [讨论点1]
2. [讨论点2]

**决策事项**
- [决策1]
- [决策2]

**行动项**
- [ ] [待办事项1] (负责人：XXX)
- [ ] [待办事项2] (负责人：XXX)

**下次会议**
[如果有，说明时间和议题]"""
    
    def _parse_todo_response(self, response: str) -> Dict[str, List[str]]:
        """解析待办整理响应"""
        # 简单解析，提取不同优先级的任务
        organized = {
            "high": [],
            "medium": [],
            "low": []
        }
        
        # TODO: 实现更智能的解析逻辑
        # 目前返回原始响应
        organized["raw"] = response
        
        return organized


# 全局服务实例
_work_service: Optional[WorkService] = None


def get_work_service() -> WorkService:
    """获取工作服务实例"""
    global _work_service
    if _work_service is None:
        _work_service = WorkService()
    return _work_service
