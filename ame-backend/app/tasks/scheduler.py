"""
任务调度器
使用 APScheduler 管理定时任务
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

from app.core.logger import get_logger
from app.tasks.lifecycle import run_lifecycle_task, run_cleanup_task

logger = get_logger(__name__)


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self):
        """初始化调度器"""
        self.scheduler = AsyncIOScheduler()
        self._is_started = False
        
        logger.info("Task Scheduler initialized")
    
    def setup_tasks(self):
        """配置定时任务"""
        
        # 1. 数据生命周期管理任务 - 每天凌晨2点执行
        self.scheduler.add_job(
            run_lifecycle_task,
            CronTrigger(hour=2, minute=0),
            id="lifecycle_management",
            name="数据生命周期管理",
            replace_existing=True
        )
        logger.info("Scheduled task: lifecycle_management at 02:00 daily")
        
        # 2. 数据清理任务 - 每周日凌晨3点执行
        self.scheduler.add_job(
            run_cleanup_task,
            CronTrigger(day_of_week=6, hour=3, minute=0),
            id="data_cleanup",
            name="过期数据清理",
            replace_existing=True
        )
        logger.info("Scheduled task: data_cleanup at 03:00 every Sunday")
        
        # 3. 可以添加更多定时任务
        # self.scheduler.add_job(
        #     some_other_task,
        #     CronTrigger(...),
        #     id="task_id",
        #     name="任务名称"
        # )
    
    def start(self):
        """启动调度器"""
        if not self._is_started:
            self.setup_tasks()
            self.scheduler.start()
            self._is_started = True
            logger.info("Task Scheduler started")
        else:
            logger.warning("Task Scheduler already started")
    
    def shutdown(self):
        """关闭调度器"""
        if self._is_started:
            self.scheduler.shutdown()
            self._is_started = False
            logger.info("Task Scheduler shutdown")
        else:
            logger.warning("Task Scheduler not running")
    
    def list_jobs(self):
        """列出所有任务"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        return jobs
    
    async def run_job_now(self, job_id: str):
        """立即执行指定任务"""
        job = self.scheduler.get_job(job_id)
        if job:
            logger.info(f"Manually triggering job: {job_id}")
            await job.func()
            return True
        else:
            logger.warning(f"Job not found: {job_id}")
            return False


# 全局调度器实例
_scheduler: TaskScheduler = None


def get_scheduler() -> TaskScheduler:
    """获取调度器实例"""
    global _scheduler
    if _scheduler is None:
        _scheduler = TaskScheduler()
    return _scheduler


def start_scheduler():
    """启动调度器"""
    scheduler = get_scheduler()
    scheduler.start()


def shutdown_scheduler():
    """关闭调度器"""
    scheduler = get_scheduler()
    scheduler.shutdown()
