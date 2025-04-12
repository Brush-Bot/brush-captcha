from datetime import datetime

worker_pool = {}

def register_worker(worker_id, ws, data):
    worker_pool[worker_id] = {
        "id": worker_id,
        "ws": ws,
        "task_types": data["task_types"],
        "max_concurrency": data["max_concurrency"],
        "current_tasks": 0,
        "pending_tasks": 0,
        "connected_at": datetime.utcnow(),
        "last_ping": datetime.utcnow(),
        "ip": ws.client.host,
    }

def update_worker_status(worker_id, status):
    # print(f"[update_worker_status]:{worker_id}: {status}")
    if worker_id in worker_pool:
        worker_pool[worker_id]["current_tasks"] = status.get("current_tasks", 0)
        # print(f"[update_worker_status]:{worker_pool[worker_id]['current_tasks'] }")
        worker_pool[worker_id]["pending_tasks"] = status.get("pending_tasks", 0)
        worker_pool[worker_id]["last_ping"] = datetime.utcnow()

def get_worker_status(info):
    if info["current_tasks"] + info["pending_tasks"] == 0:
        status = "空闲"
    elif info["current_tasks"] >= info["max_concurrency"]:
        status = "忙碌"
    else:
        status = "工作中"
    return {
        **info,
        "status": status,
        "uptime": str(datetime.utcnow() - info["connected_at"]),
    }
