"""
Prometheus 监控指标中间件
收集HTTP请求指标和业务指标
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from time import time
from typing import Callable

# ==================== HTTP 请求指标 ====================

http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0)
)

http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'Number of HTTP requests in progress',
    ['method', 'endpoint']
)

# ==================== 业务指标 ====================

faiss_index_size = Gauge(
    'faiss_index_total_vectors',
    'Total number of vectors in Faiss index'
)

metadata_db_documents = Gauge(
    'metadata_db_total_documents',
    'Total number of documents in metadata database'
)

graph_db_nodes = Gauge(
    'graph_db_total_nodes',
    'Total number of nodes in graph database'
)

search_operations_total = Counter(
    'search_operations_total',
    'Total number of search operations',
    ['search_type', 'status']
)

document_operations_total = Counter(
    'document_operations_total',
    'Total number of document operations',
    ['operation', 'doc_type', 'status']
)

# ==================== 中间件 ====================

class MetricsMiddleware(BaseHTTPMiddleware):
    """HTTP指标收集中间件"""
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        # 跳过metrics端点本身
        if request.url.path == "/metrics":
            return await call_next(request)
        
        method = request.method
        endpoint = request.url.path
        
        # 标记请求开始
        http_requests_in_progress.labels(
            method=method,
            endpoint=endpoint
        ).inc()
        
        start_time = time()
        
        try:
            # 执行请求
            response = await call_next(request)
            status = response.status_code
            
        except Exception as e:
            status = 500
            raise
        
        finally:
            # 记录指标
            duration = time() - start_time
            
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status=status
            ).inc()
            
            http_requests_in_progress.labels(
                method=method,
                endpoint=endpoint
            ).dec()
        
        return response


# ==================== 业务指标更新函数 ====================

def update_storage_metrics(
    faiss_count: int,
    metadata_count: int,
    graph_count: int
):
    """更新存储层指标"""
    faiss_index_size.set(faiss_count)
    metadata_db_documents.set(metadata_count)
    graph_db_nodes.set(graph_count)


def record_search_operation(
    search_type: str,
    success: bool
):
    """记录检索操作"""
    search_operations_total.labels(
        search_type=search_type,
        status="success" if success else "failure"
    ).inc()


def record_document_operation(
    operation: str,
    doc_type: str,
    success: bool
):
    """记录文档操作"""
    document_operations_total.labels(
        operation=operation,
        doc_type=doc_type,
        status="success" if success else "failure"
    ).inc()


# ==================== Metrics 端点 ====================

async def metrics_endpoint():
    """Prometheus metrics 端点"""
    return Response(
        content=generate_latest(),
        media_type="text/plain; version=0.0.4; charset=utf-8"
    )
