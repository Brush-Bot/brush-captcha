from fastapi import FastAPI
from api_server.routes import create_router
from api_server.ws_router import router as ws_router
from core.task_manager import cleanup_expired_tasks
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from core.task_dispatcher import scheduler_loop
from common.logger import get_logger,emoji
from user.users_manager import ClientKeyStore
logger = get_logger("main")
store = ClientKeyStore()
# logger.info(emoji("STARTUP","开始启动"))
tags_metadata = [
    {
        "name": "Task",
        "description": "打码任务创建和结果获取，兼容capsolver接口",
    },
    {
        "name": "REST",
        "description": "worker节点与任务状态查询,用于前端显示",
    },
    {
        "name": "WebSocket",
        "description": "worker节点注册、状态更新、上报数据、分发任务",
    }
]
app = FastAPI(title="Backend",
    description="HTTP + WS API",
    version="1.0.0",
    openapi_tags=tags_metadata
    )
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(create_router(store))
app.include_router(ws_router)

@app.on_event("startup")
async def startup():
    await store.load()
    logger.debug(store.get_all())
    asyncio.create_task(cleanup_expired_tasks())
    asyncio.create_task(scheduler_loop())

# print(app.routes)

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
