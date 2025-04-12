import asyncio

from core.task_manager import task_pool,Status
from core.worker_manager import worker_pool
from common.logger import get_logger,emoji
logger = get_logger("task_dispatcher")
# 以任务循环，适合少量机器，保证最优空闲调度
async def dispatch_tasks_by_tasks():
    for task in task_pool.values():
        if task["status"] != Status.WAITING:
            continue
        # 找出支持任务类型、且未满载的 worker
        candidates = [
            (wid, w) for wid, w in worker_pool.items()
            if task["type"] in w["task_types"]
            and w["current_tasks"] < w["max_concurrency"]
        ]

        if not candidates:
            continue  # 暂无可接此任务的 worker

        # 计算空闲数并按空闲数降序排序（空闲多的排前）
        candidates.sort(key=lambda x: x[1]["max_concurrency"] - x[1]["current_tasks"], reverse=True)

        worker_id, worker = candidates[0]

        try:
            await worker["ws"].send_json({
                "type": "new_task",
                "task": {
                    "taskId": task["taskId"],
                    **task["payload"]
                }
            })
            task["status"] = Status.PENDING
            task["assignedTo"] = worker_id
            worker["current_tasks"] += 1
            logger.info(f"📤 分发任务 {task['taskId']} → {worker_id}")
        except Exception as e:
            logger.info(f"❌ 发送失败 {worker_id}: {e}")
            continue
# 以worker循环，适合大量worker
async def dispatch_tasks_by_worker():
    for worker_id, worker in worker_pool.items():
        available_slots = worker["max_concurrency"] - worker["current_tasks"]
        if available_slots <= 0:
            continue

        for task in task_pool.values():
            if task["status"] != Status.WAITING:
                continue
            if task["type"] not in worker["task_types"]:
                continue

            # 找到一个可派发任务
            try:
                await worker["ws"].send_json({
                    "type": "new_task",
                    "task": {
                        "taskId": task["taskId"],
                        **task["payload"]
                    }
                })
                task["status"] = Status.PENDING
                task["assignedTo"] = worker_id
                worker["current_tasks"] += 1
                logger.info(f"📤 分发任务 {task['taskId']} → {worker_id}")
                break  # 只给这个 worker 分一个任务，避免一次性全发
            except Exception as e:
                logger.info(f"❌ 分发失败: {e}")
                continue
# 主循环
async def scheduler_loop():
    while True:
        try:
            await dispatch_tasks_by_worker()
        except Exception as e:
            logger.error(f"❌ 调度器异常：{e}")
        await asyncio.sleep(0.3) # 分发频率