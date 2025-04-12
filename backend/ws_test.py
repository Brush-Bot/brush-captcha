import asyncio
import websockets
import json
import random
import base64

WORKER_ID = "worker-1"
SERVER_URL = f"wss://capsolver.yxschool.cc:8998/ws/worker/{WORKER_ID}"

# 模拟解码逻辑
async def fake_solve(task_data):
    print(task_data)
    print("🧠 正在解码任务：", task_data["taskId"])
    await asyncio.sleep(2)  # 模拟处理耗时
    return {"token": "solved_" + str(random.randint(1000, 9999))}

async def worker_main():
    async with websockets.connect(SERVER_URL) as ws:
        # 注册能力
        await ws.send(json.dumps({
            "type": "register",
            "worker_id": WORKER_ID,
            "max_concurrency": 2,
            "task_types": ["ImageToTextTask","AntiTurnstileTaskProxyLess"]
        }))
        print("✅ 注册成功")

        # 启动心跳 + 状态更新任务
        async def heartbeat_loop():
            while True:
                await ws.send(json.dumps({
                    "type": "status_update",
                    "current_tasks": 0,
                    "pending_tasks": 0
                }))
                await asyncio.sleep(10)

        # 启动任务请求循环
        async def task_request_loop():
            while True:
                await ws.send(json.dumps({
                    "type": "request_task",
                    "ready_slots": 1
                }))
                await asyncio.sleep(3)

        # 接收任务与消息监听
        async def receive_loop():
            while True:
                msg = await ws.recv()
                data = json.loads(msg)
                if data["type"] == "new_task":
                    print(data)
                    task_id = data["task"]["taskId"]
                    task = data["task"]
                    result = await fake_solve(task)
                    await ws.send(json.dumps({
                        "type": "task_result",
                        "taskId": task_id,
                        "result": result
                    }))
                    print(f"✅ 任务完成上报：{task_id} => {result}")

        await asyncio.gather(
            heartbeat_loop(),
            task_request_loop(),
            receive_loop()
        )

if __name__ == "__main__":
    asyncio.run(worker_main())