from datetime import datetime
from enum import IntEnum
from typing import Optional, List, Dict

from pydantic import BaseModel

from app.core.config import get_settings
from app.core.logger import get_logger
from app.core.exceptions import ConfigurationError
from app.database.sqlite.schema import get_sqlite_db
from app.models.base_enums import TaskPriority, TaskStatus

logger = get_logger(__name__)


class Task(BaseModel):
    """任务实体"""
    id: Optional[int] = None
    name: str
    priority: int
    status: int


class TaskService:
    """任务"""

    def __init__(self):
        settings = get_settings()
        self.db = get_sqlite_db()

        # 检查配置
        # if not settings.is_configured:
        #     raise ConfigurationError(
        #         message="Work service not configured",
        #         detail="Please configure OpenAI API Key first"
        #     )

    async def analysis_task_desc(self, task_desc):
        """根据任务描述获取任务记录"""
        # todo chenchenaq 这里调用ame方法获取到了任务列表。。。
        task_records = [{'name': '任务1', 'priority': 1, 'status': 0}]
        # 任务列表入库
        tasks: List[Task] = [Task(**record) for record in task_records]

        if not tasks:
            logger.warning("未提取出任务列表")
            return []

        try:
            now = datetime.now().isoformat()
            data_list = []
            for task in tasks:
                data_list.append({
                    'name': task.name,
                    'priority': task.priority,
                    'status': task.status,
                    'create_time': now,
                    'update_time': now
                })

            self.db.task.insert_many(data_list)
            return True
        except Exception as e:
            logger.error(f"批量新增任务失败: {e}, tasks数量: {len(tasks)}", exc_info=True)
            raise e

    async def get_task_list(self, page, size):
        """获取任务列表"""
        if page < 1 or size < 1:
            raise ValueError("page 和 size 必须大于 0")

        offset = (page - 1) * size

        try:
            # 查询总数量
            total = self.db.task.count()

            # 查询当前页数据
            result = self.db.task.select(
                order_by="priority, update_time DESC",
                limit=size,
                offset=offset
            )
            items: List[Task] = [Task(**row) for row in result]
            enhanced_items = []
            for task in items:
                enhanced_items.append({
                    "id": task.id,
                    "name": task.name,
                    "priority": TaskPriority.to_label(task.priority),
                    "status": TaskStatus.to_label(task.status)
                })

            return {
                "items": enhanced_items,
                "total": total,
                "page": page,
                "size": size
            }

        except Exception as e:
            logger.error(f"数据库分页查询失败 - page={page}, size={size}", exc_info=True)
            raise RuntimeError(f"查询任务列表失败: {str(e)}") from e

    async def update_task_by_id(self, id, name, priority, status):
        """更新任务"""
        if id is None:
            raise ValueError("Task.id 不能为空，无法执行更新操作")
        try:
            now = datetime.now().isoformat()
            data = {
                'name': name,
                'priority': priority,
                'status': status,
                'update_time': now
            }
            self.db.task.update(data, where={'id': id})
            return True
        except Exception as e:
            logger.error(f"更新任务失败: {e}")
            raise e


_task_service: Optional[TaskService] = None


def get_task_service() -> TaskService:
    """获取工作服务实例"""
    global _task_service
    if _task_service is None:
        _task_service = TaskService()
    return _task_service
