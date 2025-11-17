"""
生活场景 API 路由
提供生活相关的智能辅助功能接口
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.services.life_service import get_life_service, LifeService
from app.core.logger import get_logger
from app.models.requests import (
    MoodAnalysisRequest,
    TrackInterestsRequest,
    LifeSummaryRequest,
    LifeSuggestionsRequest,
    RecordLifeEventRequest
)
from app.models.responses import (
    MoodAnalysisResponse,
    InterestTrackingResponse,
    LifeSummaryResponse,
    LifeSuggestionsResponse,
    RecordLifeEventResponse
)

logger = get_logger(__name__)

router = APIRouter()


@router.post("/analyze-mood", response_model=MoodAnalysisResponse)
async def analyze_mood(
    request: MoodAnalysisRequest,
    service: LifeService = Depends(get_life_service)
):
    """
    分析心情日记
    
    对用户的心情记录进行深度情绪分析，提供情绪识别、建议和关注点。
    """
    logger.info("API: Analyze mood entry")
    
    try:
        # 解析时间
        entry_time = datetime.fromisoformat(request.entry_time) if request.entry_time else None
        
        # 调用服务
        result = await service.analyze_mood(
            mood_entry=request.mood_entry,
            entry_time=entry_time
        )
        
        return MoodAnalysisResponse(**result)
        
    except Exception as e:
        logger.error(f"Failed to analyze mood: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/track-interests", response_model=InterestTrackingResponse)
async def track_interests(
    period_days: int = 30,
    service: LifeService = Depends(get_life_service)
):
    """
    追踪兴趣爱好
    
    分析指定时间范围内的生活记录，提取和追踪用户的兴趣爱好变化。
    """
    logger.info(f"API: Track interests for {period_days} days")
    
    try:
        result = await service.track_interests(
            period_days=period_days
        )
        
        return InterestTrackingResponse(**result)
        
    except Exception as e:
        logger.error(f"Failed to track interests: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/life-summary", response_model=LifeSummaryResponse)
async def generate_life_summary(
    request: LifeSummaryRequest,
    service: LifeService = Depends(get_life_service)
):
    """
    生成生活总结
    
    根据指定周期（周/月/年）生成生活总结报告。
    """
    logger.info(f"API: Generate {request.period} life summary")
    
    try:
        # 验证周期
        if request.period not in ["week", "month", "year"]:
            raise HTTPException(status_code=400, detail="Invalid period. Must be 'week', 'month', or 'year'")
        
        result = await service.generate_life_summary(
            period=request.period
        )
        
        return LifeSummaryResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate life summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/suggestions", response_model=LifeSuggestionsResponse)
async def get_life_suggestions(
    request: LifeSuggestionsRequest,
    service: LifeService = Depends(get_life_service)
):
    """
    获取生活建议
    
    基于用户的生活记录和当前情况，提供个性化的生活改善建议。
    """
    logger.info("API: Get life suggestions")
    
    try:
        result = await service.get_life_suggestions(
            context=request.context
        )
        
        return LifeSuggestionsResponse(**result)
        
    except Exception as e:
        logger.error(f"Failed to get life suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/record-event", response_model=RecordLifeEventResponse)
async def record_life_event(
    request: RecordLifeEventRequest,
    service: LifeService = Depends(get_life_service)
):
    """
    记录生活事件
    
    保存重要的生活事件到记忆系统中。
    """
    logger.info(f"API: Record life event: {request.event_type}")
    
    try:
        # 解析时间
        event_time = datetime.fromisoformat(request.event_time) if request.event_time else None
        
        result = await service.record_life_event(
            event_content=request.event_content,
            event_type=request.event_type,
            event_time=event_time,
            tags=request.tags
        )
        
        return RecordLifeEventResponse(**result)
        
    except Exception as e:
        logger.error(f"Failed to record life event: {e}")
        raise HTTPException(status_code=500, detail=str(e))
