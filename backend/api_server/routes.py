from fastapi import APIRouter
from fastapi.responses import JSONResponse
from schemas.task import CreateTaskRequest, GetTaskRequest
from core.task_manager import task_pool
from core.worker_manager import worker_pool, get_worker_status
from uuid import uuid4
from datetime import datetime
from datetime import datetime, timedelta, timezone
from fastapi.encoders import jsonable_encoder
from core.task_dispatcher import Status
from core.task_stats import task_stats
from common.logger import get_logger,emoji
logger = get_logger("routes")
router = APIRouter()

CST = timezone(timedelta(hours=8))

def serialize_worker(info):
    connected_at = info.get("connected_at")

    if connected_at and connected_at.tzinfo is None:
        connected_at = connected_at.replace(tzinfo=timezone.utc)

    return {
        "id": info.get("id"),
        "ip": info.get("ip", "unknown"),
        "task_types": info.get("task_types", []),
        "max_concurrency": info.get("max_concurrency", 0),
        "current_tasks": info.get("current_tasks", 0),
        "pending_tasks": info.get("pending_tasks", 0),
        "connected_at": connected_at.astimezone(CST).strftime("%Y-%m-%d %H:%M:%S") if connected_at else None,
        "uptime": str((datetime.now(tz=CST) - connected_at.astimezone(CST)).seconds) + " 秒" if connected_at else "N/A",
        "status": get_worker_status(info)["status"]
    }

@router.post("/createTask",tags=["Task"])
async def create_task(req: CreateTaskRequest):
    task_id = str(uuid4())
    task_pool[task_id] = {
        "taskId": task_id,
        "clientKey": req.clientKey,
        "status": Status.WAITING,
        "assignedTo": None,
        "createdAt": datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(CST).strftime("%Y-%m-%d %H:%M:%S"),
        "type": req.task.get("type", "Unknown"),
        "payload": req.task,
        "errorId": 0
    }
    await task_stats.increment_total()
    return {"errorId": 0, "taskId": task_id}

@router.post("/getTaskResult",tags=["Task"])
async def get_task(req: GetTaskRequest):
    task = task_pool.get(req.taskId)
    if not task:
        return JSONResponse(status_code=404, content={"errorId": 1, "errorDescription": "task not found"})
    if task["status"] == Status.SUCCESS:
        if task["errorId"] == 0:
            return {"errorId": 0,"taskId":req.taskId, "status": "ready", "solution": task["result"]}
        else:
            return {"errorId": task["errorId"], "taskId": req.taskId, "status": "ready", "solution": task["result"]}
    else:
        # return {"errorId": 0, "status": task["status"]}
        logger.debug(f"getTaskResult {task}")
        return {"errorId": 0, "status": "processing"}

@router.get("/nodes",tags=["REST"])
async def get_nodes():
    return jsonable_encoder([serialize_worker(info) for info in worker_pool.values()])

@router.get("/tasks",tags=["REST"])
async def get_tasks():
    def safe_str(val):
        try:
            return str(val)
        except:
            return "<unserializable>"

    # 过滤未完成任务
    active_tasks = [t for t in task_pool.values() if t.get("status") != Status.SUCCESS]

    # 汇总统计
    summary = await task_stats.get_stats()
    assigned = sum(1 for t in active_tasks if t.get("assignedTo"))

    return {
        "summary": {
            "total": summary["total"],
            "completed": summary["completed"],
            "pending": summary["pending"],
            "assigned": assigned,
        },
        "tasks": jsonable_encoder([
            {
                "taskId": t.get("taskId"),
                "status": t.get("status"),
                "assignedTo": safe_str(t.get("assignedTo")),
                "createdAt": (
                                t.get("createdAt").isoformat() if isinstance(t.get("createdAt"), datetime)
                                else t.get("createdAt") if t.get("createdAt")
                                else None
                            ),
                "type": t.get("type")
            }
            for t in active_tasks
        ])
    }
