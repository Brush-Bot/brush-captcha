import asyncio
from datetime import datetime, timedelta
from enum import Enum
from common.logger import get_logger,emoji
logger = get_logger("task_manager")
task_pool = {}
TASK_TIMEOUT_SECONDS = 300 #任务超时时间
class Status(Enum):
    PENDING = "processing"
    WAITING = "idle"
    SUCCESS = "ready"
    TIMEOUT = "timeout"

async def cleanup_expired_tasks():
    while True:
        # 剔除超时和成功的
        now = datetime.utcnow()
        expired = [
            task_id for task_id, t in task_pool.items()
            if t['status'] != Status.SUCCESS and (now - t['createdAt']).total_seconds() > TASK_TIMEOUT_SECONDS
            # if (now - t['createdAt']).total_seconds() > TASK_TIMEOUT_SECONDS
        ]
        for task_id in expired:
            # task_pool[task_id]['status'] = Status.TIMEOUT
            del task_pool[task_id]

        await asyncio.sleep(30)
