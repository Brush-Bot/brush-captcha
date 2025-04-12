import asyncio
import websockets
import json
import yaml
import importlib
import concurrent.futures
from framework.solver_core import get_solver_config
from system_resources import auto_concurrency

with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

MAX_CONCURRENCY = config.get("concurrency") or auto_concurrency()
task_queue = asyncio.Queue()
semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
executor = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CONCURRENCY)

print("最大允许线程数:", MAX_CONCURRENCY)
async def run_task(task):
    # print(f"[run_task] task = {task}")
    handler = importlib.import_module(f"task_handlers.{task['type']}")
    # print(f"[run_task] handler module loaded = {handler}")

    if asyncio.iscoroutinefunction(handler.run):
        result = await handler.run(task)
        # print(f"[run_task] handler result is coroutine = {result}")
        while asyncio.iscoroutine(result):  # 防止返回嵌套 coroutine
            result = await result
        return result
    else:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, handler.run, task)

async def task_worker(ws):
    while True:
        task = await task_queue.get()
        async with semaphore:
            try:
                result = await run_task(task)
                await ws.send(json.dumps({
                    "type": "task_result",
                    "taskId": task["taskId"],
                    "result": result
                }))
            except Exception as e:
                await ws.send(json.dumps({
                    "type": "task_result",
                    "taskId": task.get("taskId"),
                    "result": {"error": str(e)}
                }))
        task_queue.task_done()

async def heartbeat(ws):
    while True:
        running_tasks = MAX_CONCURRENCY - semaphore._value
        waiting_tasks = task_queue.qsize()
        msg = {"type": "status_update", "current_tasks": running_tasks+waiting_tasks, "pending_tasks": running_tasks}
        print(f"[heartbeat] msg = {msg}")
        await ws.send(json.dumps(msg))
        await asyncio.sleep(10)

async def receiver(ws):
    while True:
        msg = await ws.recv()
        task = json.loads(msg).get("task")
        print(f"📥 接收到任务: {task['type']} - {task['taskId']}")
        await task_queue.put(task)

async def worker_main():
    uri = config.get("worker").get("wss_url") + config.get("worker").get("name")
    while True:
        try:
            async with websockets.connect(uri) as ws:
                await ws.send(json.dumps({
                    "type": "register",
                    "task_types": get_solver_config().get("solver_type"),
                    "max_concurrency": MAX_CONCURRENCY
                }))
                print(f"✅ 已注册:{uri}")

                await asyncio.gather(
                    heartbeat(ws),
                    receiver(ws),
                    *[task_worker(ws) for _ in range(MAX_CONCURRENCY)]
                )
        except Exception as e:
            print(f"❌ 连接断开，原因: {e}")
            print("⏳ 5 秒后重试连接...")
            await asyncio.sleep(5)
