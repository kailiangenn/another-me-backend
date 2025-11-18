"""
API 请求数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str = Field(..., description="用户消息")
    context: Optional[str] = Field(None, description="对话上下文")


class LearnRequest(BaseModel):
    """学习请求模型"""
    message: str = Field(..., description="要学习的消息")
    context: Optional[str] = Field(None, description="消息上下文")


class SearchRequest(BaseModel):
    """检索请求模型"""
    query: str = Field(..., description="检索查询")
    top_k: int = Field(5, description="返回结果数量")


class ConfigRequest(BaseModel):
    """配置请求模型"""
    # 此处配置信息与config.json文件中定义的变量一致
    api_key: str = Field(..., description="OpenAI API Key")
    base_url: Optional[str] = Field("https://api.openai.com/v1", description="API 基础 URL")
    model: Optional[str] = Field("gpt-3.5-turbo", description="模型名称")
    embedding_model: Optional[str] = Field(None, description="Embedding 模型名称")
    embedding_dimension: Optional[int] = Field(None, description="Embedding 维度")


class ConfigTestRequest(BaseModel):
    """配置测试请求模型"""
    api_key: str
    base_url: str
    model: str
    embedding_model: Optional[str] = None
    embedding_dimension: Optional[int] = None


# ==================== Work Scene Requests ====================

class WeeklyReportRequest(BaseModel):
    """周报生成请求"""
    start_date: Optional[str] = Field(None, description="开始日期 YYYY-MM-DD")
    end_date: Optional[str] = Field(None, description="结束日期 YYYY-MM-DD")


class DailyReportRequest(BaseModel):
    """日报生成请求"""
    date: Optional[str] = Field(None, description="日期 YYYY-MM-DD，默认今天")


class OrganizeTodosRequest(BaseModel):
    """待办整理请求"""
    todos: List[str] = Field(..., description="原始待办事项列表")


class MeetingSummaryRequest(BaseModel):
    """会议总结请求"""
    meeting_notes: str = Field(..., description="会议记录内容")
    meeting_info: Optional[dict] = Field(None, description="会议信息（标题、时间、参与者等）")


class ProjectProgressRequest(BaseModel):
    """项目进度请求"""
    project_name: str = Field(..., description="项目名称")

class ProjectAnalysisRequest(BaseModel):
    """项目分析请求"""
    project_desc: str = Field(..., description="项目描述")

class  TaskUpdateRequest(BaseModel):
    """任务更新请求"""
    task_id: int = Field(..., description="任务ID")
    task_name: str = Field(..., description="任务名称")
    priority: int = Field(..., description="任务优先级")
    status: int = Field(..., description="任务状态")

class  TaskAnalysisRequest(BaseModel):
    """任务分析请求"""
    task_desc: str = Field(..., description="任务描述")



# ==================== Life Scene Requests ====================

class MoodAnalysisRequest(BaseModel):
    """心情分析请求"""
    mood_entry: str = Field(..., description="心情记录内容")
    entry_time: Optional[str] = Field(None, description="记录时间 ISO格式")


class TrackInterestsRequest(BaseModel):
    """兴趣追踪请求"""
    period_days: int = Field(30, description="统计时间范围（天）", ge=1, le=365)


class LifeSummaryRequest(BaseModel):
    """生活总结请求"""
    period: str = Field("week", description="总结周期: week/month/year")


class LifeSuggestionsRequest(BaseModel):
    """生活建议请求"""
    context: Optional[str] = Field(None, description="上下文信息（当前困扰、目标等）")


class RecordLifeEventRequest(BaseModel):
    """生活事件记录请求"""
    event_content: str = Field(..., description="事件内容")
    event_type: str = Field("general", description="事件类型")
    event_time: Optional[str] = Field(None, description="事件时间 ISO格式")
    tags: Optional[List[str]] = Field(None, description="标签列表")
