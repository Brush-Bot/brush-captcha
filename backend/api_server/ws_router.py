from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from core.task_stats import task_stats
from core.worker_manager import register_worker, update_worker_status, worker_pool
from core.task_manager import task_pool
from datetime import datetime
from core.task_manager import Status
from common.logger import get_logger,emoji
logger = get_logger("ws_routes")
router = APIRouter()
@router.websocket("/worker/{worker_id}")
async def worker_ws(ws: WebSocket, worker_id: str):
    await ws.accept()
    try:
        while True:
            msg = await ws.receive_json()
            logger.debug(f"received message: {msg}")
            if msg["type"] == "register":
                register_worker(worker_id, ws, msg)
            elif msg["type"] == "status_update":
                update_worker_status(worker_id, msg)
            elif msg["type"] == "task_result":
                logger.debug(f"Task result: {msg}")
                task_id = msg["taskId"]
                error_id = msg["errorId"]
                if task_id in task_pool:
                    task_pool[task_id]["status"] = Status.SUCCESS
                    task_pool[task_id]["errorId"] = error_id
                    task_pool[task_id]["result"] = msg["result"]
                    await task_stats.increment_completed()
                    # if error_id != 0:
                    #     task_pool[task_id]["status"] = Status.SUCCESS
                    #     task_pool[task_id]["errorId"] = error_id
                    #     task_pool[task_id]["result"] = msg["result"]
                    #     await task_stats.increment_completed()
                    # else:
                    #     task_pool[task_id]["status"] = Status.SUCCESS
                    #     task_pool[task_id]["errorId"] = 0
                    #     task_pool[task_id]["result"] = msg["result"]
                    #     await task_stats.increment_completed()
    except WebSocketDisconnect:
        worker_pool.pop(worker_id, None)
