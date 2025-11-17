"""
性能测试基准套件
测试Another Me系统的关键性能指标
"""
import pytest
import asyncio
from time import time
from statistics import mean, median
from typing import List

from ame.repository.hybrid_repository import HybridRepository
from ame.models.domain import Document, DocumentType
from datetime import datetime


@pytest.mark.performance
class TestPerformance:
    """性能测试套件"""
    
    @pytest.fixture
    async def repository(self):
        """准备测试仓库"""
        repo = HybridRepository(
            faiss_index_path="./data/test/faiss.index",
            metadata_db_path="./data/test/metadata.db",
            graph_db_path="./data/test/graph.db"
        )
        
        # 预加载测试数据
        await self._load_test_data(repo, count=1000)
        
        yield repo
        
        # 清理
        await repo.close()
    
    async def _load_test_data(self, repo, count: int = 1000):
        """加载测试数据"""
        documents = []
        for i in range(count):
            doc = Document(
                content=f"测试文档 {i}",
                doc_type=DocumentType.RAG_KNOWLEDGE,
                source="test",
                timestamp=datetime.now(),
                embedding=[0.1 + i * 0.001] * 1536,
                entities=[f"实体{i}"]
            )
            documents.append(doc)
        
        # 批量创建
        tasks = [repo.create(doc) for doc in documents]
        await asyncio.gather(*tasks)
    
    # ==================== 检索性能测试 ====================
    
    async def test_search_latency_baseline(self, repository):
        """测试基线检索延迟"""
        query = "测试查询"
        embedding = [0.15] * 1536
        
        # 预热（避免冷启动影响）
        for _ in range(10):
            await repository.hybrid_search(query, embedding, top_k=10)
        
        # 正式测试
        latencies = []
        iterations = 100
        
        for _ in range(iterations):
            start = time()
            results = await repository.hybrid_search(query, embedding, top_k=10)
            latency = (time() - start) * 1000  # 转换为ms
            latencies.append(latency)
            assert len(results) > 0, "检索结果不应为空"
        
        # 统计分析
        avg_latency = mean(latencies)
        median_latency = median(latencies)
        p95_latency = sorted(latencies)[int(iterations * 0.95)]
        p99_latency = sorted(latencies)[int(iterations * 0.99)]
        
        print(f"\n=== 检索延迟基准 ===")
        print(f"平均延迟: {avg_latency:.2f}ms")
        print(f"中位数延迟: {median_latency:.2f}ms")
        print(f"P95延迟: {p95_latency:.2f}ms")
        print(f"P99延迟: {p99_latency:.2f}ms")
        
        # 性能断言
        assert avg_latency < 100, f"平均延迟过高: {avg_latency:.2f}ms"
        assert p95_latency < 200, f"P95延迟过高: {p95_latency:.2f}ms"
    
    async def test_search_throughput(self, repository):
        """测试检索吞吐量"""
        query = "测试查询"
        embedding = [0.15] * 1536
        duration = 10  # 测试10秒
        
        queries_completed = 0
        start_time = time()
        
        while time() - start_time < duration:
            await repository.hybrid_search(query, embedding, top_k=10)
            queries_completed += 1
        
        actual_duration = time() - start_time
        qps = queries_completed / actual_duration
        
        print(f"\n=== 检索吞吐量 ===")
        print(f"总查询数: {queries_completed}")
        print(f"测试时长: {actual_duration:.2f}s")
        print(f"QPS: {qps:.2f}")
        
        assert qps > 10, f"QPS过低: {qps:.2f}"
    
    # ==================== 并发性能测试 ====================
    
    async def test_concurrent_searches(self, repository):
        """测试并发检索性能"""
        concurrent_levels = [1, 5, 10, 20, 50]
        results = {}
        
        for concurrency in concurrent_levels:
            queries = [f"查询{i}" for i in range(concurrency)]
            embeddings = [[0.1 + i * 0.01] * 1536 for i in range(concurrency)]
            
            start = time()
            tasks = [
                repository.hybrid_search(q, emb, top_k=5)
                for q, emb in zip(queries, embeddings)
            ]
            search_results = await asyncio.gather(*tasks)
            duration = time() - start
            
            qps = concurrency / duration
            results[concurrency] = {
                "duration": duration,
                "qps": qps,
                "results_count": len(search_results)
            }
        
        print(f"\n=== 并发检索性能 ===")
        for concurrency, metrics in results.items():
            print(f"并发数={concurrency}: "
                  f"耗时={metrics['duration']:.3f}s, "
                  f"QPS={metrics['qps']:.2f}")
        
        # 验证并发能力
        assert results[50]["qps"] > 20, "高并发下QPS过低"
    
    # ==================== 写入性能测试 ====================
    
    async def test_batch_create_performance(self, repository):
        """测试批量创建性能"""
        batch_sizes = [1, 10, 50, 100]
        
        for batch_size in batch_sizes:
            documents = []
            for i in range(batch_size):
                doc = Document(
                    content=f"批量测试文档 {i}",
                    doc_type=DocumentType.RAG_KNOWLEDGE,
                    source="batch_test",
                    timestamp=datetime.now(),
                    embedding=[0.2 + i * 0.001] * 1536,
                    entities=[f"批量实体{i}"]
                )
                documents.append(doc)
            
            start = time()
            tasks = [repository.create(doc) for doc in documents]
            await asyncio.gather(*tasks)
            duration = time() - start
            
            docs_per_second = batch_size / duration
            
            print(f"\n批量大小={batch_size}: "
                  f"耗时={duration:.3f}s, "
                  f"文档/秒={docs_per_second:.2f}")
        
        # 批量操作应该有显著性能提升
        # （这里只是示例，实际需要真正的批量API）
    
    # ==================== 内存使用测试 ====================
    
    async def test_memory_usage_growth(self, repository):
        """测试内存使用增长"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 创建1000个文档
        for i in range(1000):
            doc = Document(
                content=f"内存测试文档 {i}",
                doc_type=DocumentType.RAG_KNOWLEDGE,
                source="memory_test",
                timestamp=datetime.now(),
                embedding=[0.3 + i * 0.0001] * 1536,
                entities=[f"内存实体{i}"]
            )
            await repository.create(doc)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory
        
        print(f"\n=== 内存使用 ===")
        print(f"初始内存: {initial_memory:.2f}MB")
        print(f"最终内存: {final_memory:.2f}MB")
        print(f"增长: {memory_growth:.2f}MB")
        print(f"平均每文档: {memory_growth/1000:.4f}MB")
        
        # 内存增长应该在合理范围内
        assert memory_growth < 500, f"内存增长过大: {memory_growth:.2f}MB"
    
    # ==================== 缓存效果测试 ====================
    
    async def test_cache_effectiveness(self, repository):
        """测试缓存效果（如果启用）"""
        query = "缓存测试查询"
        embedding = [0.25] * 1536
        
        # 第一次查询（冷缓存）
        start = time()
        await repository.hybrid_search(query, embedding, top_k=10)
        cold_latency = (time() - start) * 1000
        
        # 重复查询（热缓存）
        hot_latencies = []
        for _ in range(10):
            start = time()
            await repository.hybrid_search(query, embedding, top_k=10)
            hot_latencies.append((time() - start) * 1000)
        
        avg_hot_latency = mean(hot_latencies)
        speedup = cold_latency / avg_hot_latency if avg_hot_latency > 0 else 0
        
        print(f"\n=== 缓存效果 ===")
        print(f"冷缓存延迟: {cold_latency:.2f}ms")
        print(f"热缓存平均延迟: {avg_hot_latency:.2f}ms")
        print(f"加速比: {speedup:.2f}x")
        
        # 如果启用缓存，应该有显著加速
        # assert speedup > 2, f"缓存加速效果不明显: {speedup:.2f}x"


@pytest.mark.performance
class TestAPIPerformance:
    """API层性能测试"""
    
    def test_api_endpoint_latency(self, client):
        """测试API端点延迟"""
        endpoints = [
            ("/api/v1/health", "GET", None),
            ("/api/v1/rag/search", "POST", {"query": "测试", "top_k": 5}),
            ("/api/v1/work/weekly-report", "POST", {}),
        ]
        
        for path, method, payload in endpoints:
            latencies = []
            
            for _ in range(20):
                start = time()
                if method == "GET":
                    response = client.get(path)
                else:
                    response = client.post(path, json=payload)
                latency = (time() - start) * 1000
                latencies.append(latency)
                
                assert response.status_code in [200, 201], \
                    f"{path} returned {response.status_code}"
            
            avg_latency = mean(latencies)
            print(f"\n{method} {path}: {avg_latency:.2f}ms")
            
            assert avg_latency < 500, f"{path} 延迟过高: {avg_latency:.2f}ms"


# ==================== 运行性能测试 ====================

if __name__ == "__main__":
    pytest.main([
        __file__,
        "-v",
        "-m", "performance",
        "--tb=short",
        "-s"  # 显示print输出
    ])
