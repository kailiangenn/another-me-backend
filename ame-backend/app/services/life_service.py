"""
生活场景服务
提供生活相关的AI辅助功能：心情分析、兴趣追踪、生活建议等
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import sys
from pathlib import Path

# 导入 ame 核心模块
from ame.repository.hybrid_repository import HybridRepository
from ame.models.domain import Document, DocumentType, MemoryRetentionType
from ame.engines.life_engine import LifeEngine
from ame.mem.analyze_engine import AnalyzeEngine
from ame.mem.mimic_engine import MimicEngine
from ame.llm_caller.caller import LLMCaller

from app.core.config import get_settings
from app.core.logger import get_logger
from app.core.exceptions import ConfigurationError, StorageError, LLMError

logger = get_logger(__name__)


class LifeService:
    """生活场景服务"""
    
    def __init__(self):
        """初始化生活服务"""
        settings = get_settings()
        
        # 检查配置
        if not settings.is_configured:
            raise ConfigurationError(
                message="Life service not configured",
                detail="Please configure OpenAI API Key first"
            )
        
        try:
            # 初始化 LLM Caller
            self.llm_caller = LLMCaller(
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
            # 初始化混合存储仓库
            self.repository = HybridRepository(
                faiss_index_path=str(settings.DATA_DIR / "faiss" / "life.index"),
                metadata_db_path=str(settings.DATA_DIR / "metadata" / "life.db"),
                graph_db_path=str(settings.DATA_DIR / "falkor" / "life.db")
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
        
        # 初始化生活引擎
        self.life_engine = LifeEngine(
            repository=self.repository,
            llm_caller=self.llm_caller,
            analyze_engine=self.analyzer
        )
        
        logger.info("Life Service initialized")
    
    async def analyze_mood(
        self,
        mood_entry: str,
        entry_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        分析心情日记
        
        Args:
            mood_entry: 心情记录
            entry_time: 记录时间
            
        Returns:
            心情分析结果
        """
        logger.info("Analyzing mood entry")
        
        try:
            if entry_time is None:
                entry_time = datetime.now()
            
            # 使用 LifeEngine 分析心情
            mood_analysis = await self.life_engine.analyze_mood(
                mood_entry=mood_entry,
                user_id="default",
                entry_time=entry_time
            )
            
            # 存储心情记录
            doc = Document(
                id=f"mood_{entry_time.timestamp()}",
                content=mood_entry,
                doc_type=DocumentType.LIFE_RECORD,
                source="mood_diary",
                timestamp=entry_time,
                retention_type=MemoryRetentionType.PERMANENT,
                metadata={
                    "category": "mood",
                    "emotion": {
                        "type": mood_analysis.emotion_type,
                        "intensity": mood_analysis.emotion_intensity
                    },
                    "analysis": mood_analysis.suggestions
                }
            )
            
            await self.repository.create(doc)
            
            logger.info("Mood analyzed and stored")
            
            return {
                "success": True,
                "emotion_type": mood_analysis.emotion_type,
                "emotion_intensity": mood_analysis.emotion_intensity,
                "triggers": mood_analysis.triggers,
                "trend": mood_analysis.trend.dict() if mood_analysis.trend else None,
                "suggestions": mood_analysis.suggestions,
                "document_id": doc.id,
                "timestamp": entry_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze mood: {e}")
            raise
    
    async def track_interests(
        self,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        追踪兴趣爱好
        
        Args:
            period_days: 统计时间范围（天）
            
        Returns:
            兴趣分析结果
        """
        logger.info(f"Tracking interests for past {period_days} days")
        
        try:
            # 使用 LifeEngine 追踪兴趣
            interest_report = await self.life_engine.track_interests(
                user_id="default",
                period_days=period_days
            )
            
            logger.info("Interests tracked successfully")
            
            return {
                "success": True,
                "top_interests": [t.dict() for t in interest_report.top_interests],
                "new_interests": interest_report.new_interests,
                "declining_interests": interest_report.declining_interests,
                "recommendations": interest_report.recommendations,
                "report": interest_report.report,
                "period_days": period_days
            }
            
        except Exception as e:
            logger.error(f"Failed to track interests: {e}")
            raise
    
    async def generate_life_summary(
        self,
        period: str = "week"
    ) -> Dict[str, Any]:
        """
        生成生活总结
        
        Args:
            period: 总结周期（week/month/year）
            
        Returns:
            生活总结
        """
        logger.info(f"Generating {period} life summary")
        
        try:
            # 计算日期范围
            end_date = datetime.now()
            if period == "week":
                start_date = end_date - timedelta(days=7)
            elif period == "month":
                start_date = end_date - timedelta(days=30)
            elif period == "year":
                start_date = end_date - timedelta(days=365)
            else:
                raise ValueError(f"Invalid period: {period}")
            
            # 检索生活记录
            life_records = await self._get_life_records(start_date, end_date)
            
            if not life_records:
                return {
                    "success": False,
                    "message": "No life records found for the specified period"
                }
            
            # 使用分析引擎生成总结
            summary = await self.analyzer.generate_report(
                documents=life_records,
                report_type="life_summary",
                context={
                    "period": period,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            )
            
            logger.info("Life summary generated successfully")
            
            return {
                "success": True,
                "summary": summary,
                "period": period,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "records_count": len(life_records)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate life summary: {e}")
            raise
    
    async def get_life_suggestions(
        self,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取生活建议
        
        Args:
            context: 上下文信息（如当前困扰、目标等）
            
        Returns:
            生活建议
        """
        logger.info("Getting life suggestions")
        
        try:
            # 使用 LifeEngine 生成建议
            suggestions = await self.life_engine.generate_life_suggestions(
                user_id="default",
                context=context
            )
            
            logger.info("Life suggestions generated")
            
            return {
                "success": True,
                "suggestions": suggestions
            }
            
        except Exception as e:
            logger.error(f"Failed to get life suggestions: {e}")
            raise
    
    async def record_life_event(
        self,
        event_content: str,
        event_type: str = "general",
        event_time: Optional[datetime] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        记录生活事件
        
        Args:
            event_content: 事件内容
            event_type: 事件类型（general/achievement/memory/activity等）
            event_time: 事件时间
            tags: 标签
            
        Returns:
            记录结果
        """
        logger.info(f"Recording life event: {event_type}")
        
        try:
            if event_time is None:
                event_time = datetime.now()
            
            # 创建文档
            doc = Document(
                id=f"life_event_{event_time.timestamp()}",
                content=event_content,
                doc_type=DocumentType.LIFE_RECORD,
                source="user_input",
                timestamp=event_time,
                retention_type=MemoryRetentionType.PERMANENT,
                metadata={
                    "event_type": event_type,
                    "tags": tags or []
                }
            )
            
            # 存储到仓库
            await self.repository.create(doc)
            
            logger.info("Life event recorded successfully")
            
            return {
                "success": True,
                "document_id": doc.id,
                "event_type": event_type,
                "timestamp": event_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to record life event: {e}")
            raise
    
    # ==================== 辅助方法 ====================
    
    async def _get_life_records(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Document]:
        """
        获取指定时间范围内的生活记录
        
        使用 HybridRepository 的时间范围检索功能
        """
        # 使用时间范围检索
        docs = await self.repository.search_by_time_range(
            start_date=start_date,
            end_date=end_date,
            doc_type=DocumentType.LIFE_RECORD,
            limit=200
        )
        
        return docs
    
    async def _get_recent_life_records(self, limit: int = 20) -> List[Document]:
        """
        获取最近的生活记录
        
        使用最近 30 天的记录
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        docs = await self.repository.search_by_time_range(
            start_date=start_date,
            end_date=end_date,
            doc_type=DocumentType.LIFE_RECORD,
            limit=limit
        )
        
        return docs
    
    def _build_mood_analysis_prompt(self, mood_entry: str) -> str:
        """构建心情分析提示词"""
        return f"""请分析以下心情日记，提供深度的情绪分析和建议：

心情日记：
{mood_entry}

请按照以下格式输出：

**情绪识别**
主要情绪：[情绪类型]
情绪强度：[1-10分]

**深层分析**
[分析这段记录背后的情绪原因、触发因素等]

**积极面**
[找出记录中的积极因素或成长点]

**建议**
1. [建议1]
2. [建议2]

**关注点**
[如果发现需要关注的情绪问题，请提醒]"""
    
    def _build_suggestions_prompt(
        self,
        insights: List[Dict[str, Any]],
        context: Optional[str]
    ) -> str:
        """构建生活建议提示词"""
        insights_text = "\n".join([f"- {i.get('content', '')}" for i in insights[:5]])
        
        context_text = ""
        if context:
            context_text = f"\n当前情况：\n{context}\n"
        
        return f"""基于用户最近的生活记录，提供个性化的生活建议。

发现的模式和洞察：
{insights_text}
{context_text}

请提供3-5条具体、可行的生活建议，帮助用户：
1. 提升生活质量
2. 发展个人兴趣
3. 改善情绪状态
4. 优化时间管理

建议格式：
**建议1：[标题]**
[具体描述和行动步骤]

**建议2：[标题]**
[具体描述和行动步骤]

..."""


# 全局服务实例
_life_service: Optional[LifeService] = None


def get_life_service() -> LifeService:
    """获取生活服务实例"""
    global _life_service
    if _life_service is None:
        _life_service = LifeService()
    return _life_service
