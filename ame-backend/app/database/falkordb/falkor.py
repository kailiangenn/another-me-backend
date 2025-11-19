from falkordb import FalkorDB

from app.core.config import get_settings


class FalkorDataModel:
    def __init__(self):
        """
        初始化 FalkorDB 客户端
        """
        settings = get_settings()
        self.db = FalkorDB(host=settings.FALKOR_HOST, port=settings.FALKOR_PORT)
        self.graph = self.db.select_graph(settings.FALKOR_GRAPH_NAME)

    def query(self, cypher_query):
        """
        执行 Cypher 查询并返回结果

        :param cypher_query: Cypher 查询字符串
        :return: 查询结果（字典列表）
        """
        try:
            result = self.graph.query(cypher_query)
            # 将结果转换为字典列表（便于处理）
            return [record.__dict__ for record in result.result_set]
        except Exception as e:
            print(f"Query failed: {e}")
            return None

_falkor_db = None
def get_falkor_db() -> FalkorDataModel:
    global _falkor_db
    if _falkor_db is None:
        _falkor_db = FalkorDataModel()
    return _falkor_db
