import asyncio
from core.ws_client import worker_main

if __name__ == "__main__":
    asyncio.run(worker_main())
