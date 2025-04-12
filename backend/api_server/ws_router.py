from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from core.task_stats import task_stats
from core.worker_manager import register_worker, update_worker_status, worker_pool
from core.task_manager import task_pool
from datetime import datetime
from core.task_manager import Status
router = APIRouter()

@router.websocket("/worker/{worker_id}")
async def worker_ws(ws: WebSocket, worker_id: str):
    await ws.accept()
    try:
        while True:
            msg = await ws.receive_json()
            # print(msg)
            if msg["type"] == "register":
                register_worker(worker_id, ws, msg)
            elif msg["type"] == "status_update":
                update_worker_status(worker_id, msg)
            # elif msg["type"] == "request_task":
            #     ready_slots = msg.get("ready_slots", 1)
            #     await dispatch_tasks(worker_id, ready_slots)
            elif msg["type"] == "task_result":
                task_id = msg["taskId"]
                if task_id in task_pool:
                    task_pool[task_id]["status"] = Status.SUCCESS
                    task_pool[task_id]["result"] = msg["result"]
                    await task_stats.increment_completed()
    except WebSocketDisconnect:
        worker_pool.pop(worker_id, None)
