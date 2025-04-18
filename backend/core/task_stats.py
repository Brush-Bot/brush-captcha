import asyncio

class TaskStats:
    def __init__(self):
        self.total = 0
        self.completed = 0
        self.lock = asyncio.Lock()

    async def increment_total(self):
        async with self.lock:
            self.total += 1

    async def increment_completed(self):
        async with self.lock:
            self.completed += 1

    async def get_stats(self):
        async with self.lock:
            return {
                "total": self.total,
                "completed": self.completed,
                "pending": self.total - self.completed
            }

task_stats = TaskStats()