"""
工作场景 API 路由
提供工作相关的智能辅助功能接口
"""
from fastapi import APIRouter, HTTPException, Depends, FastAPI, Body

from app.api.v1 import config
from app.core.logger import get_logger
from app.models.requests import ProjectAnalysisRequest, TaskUpdateRequest, TaskAnalysisRequest
from app.services.project_service import get_project_service, ProjectService
from app.models.responses import ApiResponse, ApiResponseWithPageable, Pageable
from app.services.task_service import get_task_service, TaskService

logger = get_logger(__name__)

router = APIRouter()


# @router.post("/weekly-report", response_model=WeeklyReportResponse)
# async def generate_weekly_report(
#     request: WeeklyReportRequest,
#     service: WorkService = Depends(get_work_service)
# ):
#     """
#     生成工作周报
#
#     根据指定时间范围内的工作记录，自动生成周报内容。
#     如果不指定日期，则生成上一周的周报。
#     """
#     logger.info(f"API: Generate weekly report request")
#
#     try:
#         # 解析日期
#         start_date = datetime.fromisoformat(request.start_date) if request.start_date else None
#         end_date = datetime.fromisoformat(request.end_date) if request.end_date else None
#
#         # 调用服务
#         result = await service.generate_weekly_report(
#             start_date=start_date,
#             end_date=end_date
#         )
#
#         return WeeklyReportResponse(**result)
#
#     except Exception as e:
#         logger.error(f"Failed to generate weekly report: {e}")
#         raise HTTPException(status_code=500, detail=str(e))
#
#
# @router.post("/daily-report", response_model=DailyReportResponse)
# async def generate_daily_report(
#     request: DailyReportRequest,
#     service: WorkService = Depends(get_work_service)
# ):
#     """
#     生成工作日报
#
#     根据指定日期的工作记录，自动生成日报内容。
#     如果不指定日期，则生成今天的日报。
#     """
#     logger.info(f"API: Generate daily report request")
#
#     try:
#         # 解析日期
#         date = datetime.fromisoformat(request.date) if request.date else None
#
#         # 调用服务
#         result = await service.generate_daily_report(date=date)
#
#         return DailyReportResponse(**result)
#
#     except Exception as e:
#         logger.error(f"Failed to generate daily report: {e}")
#         raise HTTPException(status_code=500, detail=str(e))
#
#
# @router.post("/organize-todos", response_model=OrganizeTodosResponse)
# async def organize_todos(
#     request: OrganizeTodosRequest,
#     service: WorkService = Depends(get_work_service)
# ):
#     """
#     智能整理待办事项
#
#     对原始待办列表进行智能分类、优先级排序和去重。
#     """
#     logger.info(f"API: Organize {len(request.todos)} todos")
#
#     try:
#         result = await service.organize_todos(
#             raw_todos=request.todos
#         )
#
#         return OrganizeTodosResponse(**result)
#
#     except Exception as e:
#         logger.error(f"Failed to organize todos: {e}")
#         raise HTTPException(status_code=500, detail=str(e))
#
#
# @router.post("/summarize-meeting", response_model=MeetingSummaryResponse)
# async def summarize_meeting(
#     request: MeetingSummaryRequest,
#     service: WorkService = Depends(get_work_service)
# ):
#     """
#     总结会议内容
#
#     根据会议记录自动生成会议总结，提取关键讨论点、决策事项和行动项。
#     """
#     logger.info("API: Summarize meeting")
#
#     try:
#         result = await service.summarize_meeting(
#             meeting_notes=request.meeting_notes,
#             meeting_info=request.meeting_info
#         )
#
#         return MeetingSummaryResponse(**result)
#
#     except Exception as e:
#         logger.error(f"Failed to summarize meeting: {e}")
#         raise HTTPException(status_code=500, detail=str(e))
#
#
# @router.post("/track-project", response_model=ProjectProgressResponse)
# async def track_project_progress(
#     request: ProjectProgressRequest,
#     service: WorkService = Depends(get_work_service)
# ):
#     """
#     追踪项目进度
#
#     分析项目相关的所有工作记录，生成项目进度报告。
#     """
#     logger.info(f"API: Track project progress: {request.project_name}")
#
#     try:
#         result = await service.track_project_progress(
#             project_name=request.project_name
#         )
#
#         return ProjectProgressResponse(**result)
#
#     except Exception as e:
#         logger.error(f"Failed to track project progress: {e}")
#         raise HTTPException(status_code=500, detail=str(e))


@router.get("/project/history", response_model=ApiResponse)
async def get_history_project_analysis(
        service: ProjectService = Depends(get_project_service)
):
    """
    获取历史项目分析记录
    """
    logger.info(f"API: get_history_project_analysis...")

    try:
        result = await service.get_history_project_analysis()
        return ApiResponse.success(data=result)

    except Exception as e:
        logger.error(f"获取历史项目分析记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/project/analysis", response_model=ApiResponse)
async def analysis_project_desc(
        request: ProjectAnalysisRequest,
        service: ProjectService = Depends(get_project_service)
):
    """
    根据文本进行项目分析
    """
    logger.info(f"API: project_analysis...")

    try:
        result = await service.analysis_project_desc(request.project_desc)
        return ApiResponse.success(data=result)

    except Exception as e:
        logger.error(f"根据文本进行项目分析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/task/list", response_model=ApiResponseWithPageable)
async def task_list(
        page: int = 1, size: int = 9999,
        service: TaskService = Depends(get_task_service)
):
    """
    获取任务列表
    """
    logger.info(f"API: task_list...")

    try:
        result = await service.get_task_list(page, size)
        pageable = Pageable(total_count=result["total"], page=page, size=size)
        return ApiResponseWithPageable.success(data=result["items"], pageable=pageable)

    except Exception as e:
        logger.error(f"获取任务列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/task/update", response_model=ApiResponse)
async def update_task(
        request: TaskUpdateRequest,
        service: TaskService = Depends(get_task_service)
):
    """
    更新任务
    """
    logger.info(f"API: update_task...")

    try:
        result = await service.update_task_by_id(id=request.task_id,
                                                 name=request.task_name,
                                                 priority=request.priority,
                                                 status=request.status)
        return ApiResponse.success(data=result)

    except Exception as e:
        logger.error(f"更新任务: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/task/analysis", response_model=ApiResponse)
async def analysis_task(
        request: TaskAnalysisRequest,
        service: TaskService = Depends(get_task_service)
):
    """
    任务分析
    """
    logger.info(f"API: update_task...")

    try:
        result = await service.analysis_task_desc(request.task_desc)
        return ApiResponse.success(data=result)

    except Exception as e:
        logger.error(f"任务分析: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    app = FastAPI(title="Another Me Backend")
    app.include_router(router, prefix="/api/v1/work")
    app.include_router(config.router, prefix="/api/v1/config")
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
