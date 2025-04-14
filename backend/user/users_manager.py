# utils/client_key_store.py
import aiofiles
import asyncio
from typing import List
from asyncio import Lock
from common.logger import get_logger,emoji

logger = get_logger("users_manager")


class ClientKeyStore:
    def __init__(self, file_path: str = "user/client_keys.txt"):
        self.file_path = file_path
        self._keys: List[str] = []
        self._lock = Lock()

    async def load(self) -> None:
        async with self._lock:
            try:
                async with aiofiles.open(self.file_path, mode="r") as f:
                    content = await f.read()
                    logger.debug(content)
                self._keys = content.splitlines()
            except FileNotFoundError:
                self._keys = []

    def get_all(self) -> List[str]:
        return self._keys

    def add_key(self, key: str) -> None:
        if key not in self._keys:
            self._keys.append(key)

    def remove_key(self, key: str) -> None:
        if key in self._keys:
            self._keys.remove(key)

    async def has_key(self, key: str) -> bool:
        async with self._lock:
            return key in self._keys

    async def save(self) -> None:
        async with self._lock:
            async with aiofiles.open(self.file_path, mode="w") as f:
                await f.write("\n".join(self._keys))
