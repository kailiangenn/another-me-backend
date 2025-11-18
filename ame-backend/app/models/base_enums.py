from enum import IntEnum
from typing import Dict


class TaskStatus(IntEnum):
    """任务状态枚举"""
    PENDING = 0  # 未处理
    PROCESSING = 1  # 处理中
    COMPLETED = 2  # 已完成

    @classmethod
    def to_label(cls, value: int) -> str:
        """将状态值转为中文标签"""
        labels = {
            cls.PENDING: "未处理",
            cls.PROCESSING: "处理中",
            cls.COMPLETED: "已完成"
        }
        return labels.get(value, "未知状态")

    @classmethod
    def choices(cls) -> Dict[int, str]:
        return {
            cls.PENDING: "未处理",
            cls.PROCESSING: "处理中",
            cls.COMPLETED: "已完成"
        }


class TaskPriority(IntEnum):
    """任务优先级枚举"""
    HIGH = 2  # 高
    MEDIUM = 1  # 中
    LOW = 0  # 低

    @classmethod
    def to_label(cls, value: int) -> str:
        """将优先级值转为中文标签"""
        labels = {
            cls.HIGH: "高",
            cls.MEDIUM: "中",
            cls.LOW: "低"
        }
        return labels.get(value, f"未知优先级({value})")

    @classmethod
    def choices(cls):
        return {
            cls.HIGH: "高",
            cls.MEDIUM: "中",
            cls.LOW: "低"
        }
