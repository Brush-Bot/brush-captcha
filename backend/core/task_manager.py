import asyncio
from datetime import datetime, timedelta
from enum import Enum
from common.logger import get_logger,emoji
from datetime import datetime
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
        now = datetime.utcnow()
        expired = [
            task_id for task_id, t in task_pool.items()
            if t['status'] != Status.SUCCESS and
               (now - (
                   t['createdAt'] if isinstance(t['createdAt'], datetime)
                   else datetime.fromisoformat(t['createdAt'])
               )).total_seconds() > TASK_TIMEOUT_SECONDS
        ]
        for task_id in expired:
            del task_pool[task_id]

        await asyncio.sleep(30)
