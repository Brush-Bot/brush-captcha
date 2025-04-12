from fastapi import FastAPI
from api_server.routes import router as api_router
from api_server.ws_router import router as ws_router
from core.task_manager import cleanup_expired_tasks
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from core.task_dispatcher import scheduler_loop
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或者指定 ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)
app.include_router(ws_router)

@app.on_event("startup")
async def startup():
    asyncio.create_task(cleanup_expired_tasks())
    asyncio.create_task(scheduler_loop())
print(app.routes)


