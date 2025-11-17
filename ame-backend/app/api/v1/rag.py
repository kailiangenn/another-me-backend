"""
RAG 知识库 API
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from typing import List
import shutil
from pathlib import Path
import uuid

from app.services.rag_service import RAGService, get_rag_service
from app.models.requests import SearchRequest
from app.models.responses import (
    UploadResponse,
    SearchResponse,
    RAGStats,
    DocumentInfo,
    BaseResponse
)
from app.core.config import get_settings
from app.core.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    service: RAGService = Depends(get_rag_service)
):
    """
    上传文档到知识库
    
    Args:
        file: 上传的文件
        service: RAG 服务实例
        
    Returns:
        上传结果
    """
    settings = get_settings()
    
    # 检查文件扩展名
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_ext} not allowed"
        )
    
    # 保存上传的文件
    file_id = str(uuid.uuid4())
    file_path = settings.UPLOADS_DIR / f"{file_id}{file_ext}"
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 处理文档
        result = await service.upload_document(
            file_path=str(file_path),
            filename=file.filename
        )
        
        return UploadResponse(
            success=True,
            document_id=result["document_id"],
            filename=file.filename,
            message="Document uploaded successfully"
        )
        
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        # 清理文件
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.post("/search", response_model=SearchResponse)
async def search_knowledge(
    request: SearchRequest,
    service: RAGService = Depends(get_rag_service)
):
    """
    检索知识库
    
    Args:
        request: 检索请求
        service: RAG 服务实例
        
    Returns:
        检索结果
    """
    try:
        result = await service.search_knowledge(
            query=request.query,
            top_k=request.top_k
        )
        
        return SearchResponse(**result)
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/documents", response_model=List[DocumentInfo])
async def get_documents(
    service: RAGService = Depends(get_rag_service)
):
    """
    获取所有文档
    
    Args:
        service: RAG 服务实例
        
    Returns:
        文档列表
    """
    try:
        documents = await service.get_documents()
        return documents
        
    except Exception as e:
        logger.error(f"Get documents failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get documents: {str(e)}"
        )


@router.delete("/documents/{doc_id}", response_model=BaseResponse)
async def delete_document(
    doc_id: str,
    service: RAGService = Depends(get_rag_service)
):
    """
    删除文档
    
    Args:
        doc_id: 文档 ID
        service: RAG 服务实例
        
    Returns:
        删除结果
    """
    try:
        success = await service.delete_document(doc_id)
        
        return BaseResponse(
            success=success,
            message="Document deleted successfully" if success else "Delete failed"
        )
        
    except Exception as e:
        logger.error(f"Delete failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Delete failed: {str(e)}"
        )


@router.get("/stats", response_model=RAGStats)
async def get_stats(
    service: RAGService = Depends(get_rag_service)
):
    """
    获取知识库统计信息
    
    Args:
        service: RAG 服务实例
        
    Returns:
        统计信息
    """
    try:
        stats = await service.get_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Get stats failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )
