"""
MEM 对话 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import List

from app.services.mem_service import MEMService, get_mem_service
from app.models.requests import ChatRequest, LearnRequest
from app.models.responses import (
    ChatResponse,
    Memory,
    MemoryListResponse,
    BaseResponse
)
from app.core.logger import get_logger
from datetime import datetime

router = APIRouter()
logger = get_logger(__name__)


@router.post("/chat")
async def chat_stream(
    request: ChatRequest,
    service: MEMService = Depends(get_mem_service)
):
    """
    流式对话接口（SSE）
    
    Args:
        request: 聊天请求
        service: MEM 服务实例
        
    Returns:
        SSE 流式响应
    """
    try:
        async def event_generator():
            """生成 SSE 事件"""
            try:
                async for chunk in service.chat_stream(
                    message=request.message,
                    temperature=0.8
                ):
                    yield f"data: {chunk}\n\n"
                
                # 发送结束标记
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                logger.error(f"Stream error: {e}")
                yield f"data: [ERROR]: {str(e)}\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
        
    except RuntimeError as e:
        # API 未配置
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {str(e)}"
        )


# @router.post("/chat-sync", response_model=ChatResponse)
# async def chat(
#     request: ChatRequest,
#     service: MEMService = Depends(get_mem_service)
# ):
#     """
#     同步对话接口
#
#     Args:
#         request: 聊天请求
#         service: MEM 服务实例
#
#     Returns:
#         对话响应
#     """
#     try:
#         response = await service.chat(
#             message=request.message,
#             temperature=0.8
#         )
#
#         return ChatResponse(
#             message=response,
#             timestamp=datetime.now()
#         )
#
#     except RuntimeError as e:
#         raise HTTPException(
#             status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
#             detail=str(e)
#         )
#     except Exception as e:
#         logger.error(f"Chat failed: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Chat failed: {str(e)}"
#         )
#
#
# @router.post("/learn", response_model=BaseResponse)
# async def learn(
#     request: LearnRequest,
#     service: MEMService = Depends(get_mem_service)
# ):
#     """
#     学习对话
#
#     Args:
#         request: 学习请求
#         service: MEM 服务实例
#
#     Returns:
#         学习结果
#     """
#     try:
#         result = await service.learn_from_conversation(
#             message=request.message,
#             context=request.context
#         )
#
#         return BaseResponse(**result)
#
#     except RuntimeError as e:
#         raise HTTPException(
#             status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
#             detail=str(e)
#         )
#     except Exception as e:
#         logger.error(f"Learn failed: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Learn failed: {str(e)}"
#         )
#
#
# @router.get("/memories", response_model=MemoryListResponse)
# async def get_memories(
#     limit: int = 100,
#     service: MEMService = Depends(get_mem_service)
# ):
#     """
#     获取记忆列表
#
#     Args:
#         limit: 数量限制
#         service: MEM 服务实例
#
#     Returns:
#         记忆列表
#     """
#     try:
#         memories = await service.get_memories(limit=limit)
#
#         return MemoryListResponse(
#             memories=memories,
#             total=len(memories)
#         )
#
#     except RuntimeError as e:
#         raise HTTPException(
#             status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
#             detail=str(e)
#         )
#     except Exception as e:
#         logger.error(f"Get memories failed: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to get memories: {str(e)}"
#         )
#
#
# @router.delete("/memories/{memory_id}", response_model=BaseResponse)
# async def delete_memory(
#     memory_id: str,
#     service: MEMService = Depends(get_mem_service)
# ):
#     """
#     删除记忆
#
#     Args:
#         memory_id: 记忆 ID
#         service: MEM 服务实例
#
#     Returns:
#         删除结果
#     """
#     try:
#         success = await service.delete_memory(memory_id)
#
#         return BaseResponse(
#             success=success,
#             message="Memory deleted successfully" if success else "Delete failed"
#         )
#
#     except RuntimeError as e:
#         raise HTTPException(
#             status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
#             detail=str(e)
#         )
#     except Exception as e:
#         logger.error(f"Delete memory failed: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Delete failed: {str(e)}"
#         )
