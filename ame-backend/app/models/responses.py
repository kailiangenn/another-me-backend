"""
API 响应数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool = Field(True, description="请求是否成功")
    message: str = Field("", description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field("ok", description="服务状态")
    version: str = Field("1.0.0", description="API 版本")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")


class ChatResponse(BaseModel):
    """聊天响应模型"""
    message: str = Field(..., description="AI 回复")
    timestamp: datetime = Field(default_factory=datetime.now)


class DocumentInfo(BaseModel):
    """文档信息模型"""
    id: str = Field(..., description="文档 ID")
    filename: str = Field(..., description="文件名")
    size: int = Field(..., description="文件大小（字节）")
    upload_time: datetime = Field(default_factory=datetime.now)
    chunk_count: Optional[int] = Field(None, description="分块数量")


class UploadResponse(BaseModel):
    """上传响应模型"""
    success: bool = True
    document_id: str = Field(..., description="文档 ID")
    filename: str
    message: str = "Document uploaded successfully"


class SearchResult(BaseModel):
    """检索结果模型"""
    content: str = Field(..., description="内容")
    score: float = Field(..., description="相似度分数")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class SearchResponse(BaseModel):
    """检索响应模型"""
    query: str
    results: List[SearchResult]
    total: int = Field(..., description="结果总数")


class RAGStats(BaseModel):
    """RAG 统计信息"""
    document_count: int = Field(0, description="文档总数")
    total_chunks: int = Field(0, description="总分块数")
    total_size: int = Field(0, description="总大小（字节）")


class Memory(BaseModel):
    """记忆模型"""
    id: str
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MemoryListResponse(BaseModel):
    """记忆列表响应"""
    memories: List[Memory]
    total: int


class ConfigTestResult(BaseModel):
    """配置测试结果"""
    success: bool
    message: str
    model_available: Optional[bool] = None
    embedding_available: Optional[bool] = None
    embedding_dimension: Optional[int] = None


class ErrorResponse(BaseModel):
    """错误响应模型"""
    success: bool = False
    error: str = Field(..., description="错误信息")
    detail: Optional[str] = Field(None, description="详细错误")
    timestamp: datetime = Field(default_factory=datetime.now)


# ==================== Work Scene Responses ====================

class WeeklyReportResponse(BaseModel):
    """周报响应"""
    success: bool = True
    report: str = Field(..., description="周报内容")
    period: Dict[str, str] = Field(..., description="时间范围")
    logs_count: int = Field(..., description="工作记录数量")
    message: str = Field(default="Weekly report generated successfully")


class DailyReportResponse(BaseModel):
    """日报响应"""
    success: bool = True
    report: str = Field(..., description="日报内容")
    date: str = Field(..., description="日期")
    logs_count: int = Field(..., description="工作记录数量")
    message: str = Field(default="Daily report generated successfully")


class OrganizeTodosResponse(BaseModel):
    """待办整理响应"""
    success: bool = True
    organized_todos: Dict[str, Any] = Field(..., description="整理后的待办事项")
    original_count: int = Field(..., description="原始待办数量")
    message: str = Field(default="Todos organized successfully")


class MeetingSummaryResponse(BaseModel):
    """会议总结响应"""
    success: bool = True
    summary: str = Field(..., description="会议总结")
    document_id: str = Field(..., description="存储的文档ID")
    message: str = Field(default="Meeting summarized successfully")


class ProjectProgressResponse(BaseModel):
    """项目进度响应"""
    success: bool = True
    project_name: str = Field(..., description="项目名称")
    progress: str = Field(..., description="项目进度报告")
    records_count: int = Field(..., description="相关记录数量")
    message: str = Field(default="Project progress tracked successfully")


# ==================== Life Scene Responses ====================

class MoodAnalysisResponse(BaseModel):
    """心情分析响应"""
    success: bool = True
    analysis: str = Field(..., description="心情分析结果")
    document_id: str = Field(..., description="存储的文档ID")
    timestamp: str = Field(..., description="记录时间")
    message: str = Field(default="Mood analyzed successfully")


class InterestTrackingResponse(BaseModel):
    """兴趣追踪响应"""
    success: bool = True
    interests: List[Dict[str, Any]] = Field(..., description="兴趣列表")
    period: Dict[str, Any] = Field(..., description="时间范围")
    records_count: int = Field(..., description="分析的记录数量")
    message: str = Field(default="Interests tracked successfully")


class LifeSummaryResponse(BaseModel):
    """生活总结响应"""
    success: bool = True
    summary: str = Field(..., description="生活总结")
    period: str = Field(..., description="总结周期")
    date_range: Dict[str, str] = Field(..., description="日期范围")
    records_count: int = Field(..., description="记录数量")
    message: str = Field(default="Life summary generated successfully")


class LifeSuggestionsResponse(BaseModel):
    """生活建议响应"""
    success: bool = True
    suggestions: str = Field(..., description="生活建议")
    based_on_records: int = Field(..., description="基于的记录数量")
    insights: List[Dict[str, Any]] = Field(..., description="提取的洞察")
    message: str = Field(default="Life suggestions generated successfully")


class RecordLifeEventResponse(BaseModel):
    """生活事件记录响应"""
    success: bool = True
    document_id: str = Field(..., description="文档ID")
    event_type: str = Field(..., description="事件类型")
    timestamp: str = Field(..., description="记录时间")
    message: str = Field(default="Life event recorded successfully")

class ApiResponse(BaseModel):
    code: int = Field(..., description="状态码")
    msg: str = Field(..., description="状态消息")
    data: Any = Field(..., description="响应数据，可以是任意类型（字符串、对象等）")

    @classmethod
    def success(cls, data: Any = None) -> "ApiResponse":
        """
        构造一个成功的 API 响应。

        :param data: 任意类型的响应数据（默认为 None）
        :return: ApiResponse 实例，code=200, msg="success"
        """
        return cls(code=200, msg="success", data=data)

    @classmethod
    def error(cls, code: int, msg: str) -> "ApiResponse":
        """
        构造一个失败的 API 响应。
        :param code: 错误码
        :param msg: 错误消息
        :return: ApiResponse 实例，code=指定错误码, msg=指定错误消息
        """
        return cls(code=code, msg=msg, data=None)

class Pageable(BaseModel):
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")
    total_count: int = Field(..., description="总记录数")

class ApiResponseWithPageable(ApiResponse):
    pageable: Optional[Pageable] = Field(None, description="分页信息")

    @classmethod
    def success(
        cls,
        data: Any = None,
        pageable: Optional[Pageable] = None
    ) -> "ApiResponseWithPageable":
        return cls(code=200, msg="success", data=data, pageable=pageable)

    @classmethod
    def error(
        cls,
        code: int,
        msg: str,
        pageable: Optional[Pageable] = None
    ) -> "ApiResponseWithPageable":
        return cls(code=code, msg=msg, data=None, pageable=pageable)
