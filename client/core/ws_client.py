import asyncio
import websockets
import json
import yaml
import importlib
import concurrent.futures
from framework.solver_core import get_solver_config
from core.system_resources import auto_concurrency
from common.logger import get_logger,emoji
logger = get_logger("ws_client")
with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

MAX_CONCURRENCY = config.get("concurrency") or auto_concurrency()
task_queue = asyncio.Queue()
semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
executor = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CONCURRENCY)

logger.info(emoji("TASK",f"最大允许线程数:{MAX_CONCURRENCY}"))
async def run_task(task,proxy):
    handler = importlib.import_module(f"task_handlers.{task['type']}")
    logger.debug(f"执行的函数:{handler}")
    if asyncio.iscoroutinefunction(handler.run):
        result = await handler.run(task,proxy)
        while asyncio.iscoroutine(result):
            result = await result
        return result
    else:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, handler.run, task)

async def task_worker(ws):
    while True:
        task,proxy = await task_queue.get()
        async with semaphore:
            try:
                result = await run_task(task,proxy)
                await ws.send(json.dumps({
                    "type": "task_result",
                    "taskId": task["taskId"],
                    "errorId": 0,
                    "result": result
                }))
            except Exception as e:
                await ws.send(json.dumps({
                    "type": "task_result",
                    "taskId": task.get("taskId"),
                    "errorId":-1,
                    "result": {"error": str(e)}
                }))
        task_queue.task_done()

async def heartbeat(ws):
    while True:
        running_tasks = MAX_CONCURRENCY - semaphore._value
        waiting_tasks = task_queue.qsize()
        msg = {"type": "status_update", "current_tasks": running_tasks+waiting_tasks, "pending_tasks": running_tasks}
        await ws.send(json.dumps(msg))
        await asyncio.sleep(10)

async def receiver(ws):
    while True:
        msg = await ws.recv()
        task = json.loads(msg).get("task")
        proxy = json.loads(msg).get("proxy")
        logger.info(emoji("GETTASK",f"接收到任务: {task['type']} - {task['taskId']}"))
        await task_queue.put((task,proxy))

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
                logger.info(emoji("SUCCESS",f"已注册:{uri}"))

                await asyncio.gather(
                    heartbeat(ws),
                    receiver(ws),
                    *[task_worker(ws) for _ in range(MAX_CONCURRENCY)]
                )
        except Exception as e:
            logger.info(emoji("ERROR", f"连接断开，原因: {e}"))
            logger.info(emoji("WAIT", "5 秒后重试连接..."))
            await asyncio.sleep(5)
