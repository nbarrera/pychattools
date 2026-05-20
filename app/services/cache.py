import json
from typing import Callable, Awaitable, Any
import redis.asyncio as redis

from app.config import settings


class Cache:
    def __init__(self, url: str):
        self._client = redis.from_url(url)

    async def find(
        self,
        key: str,
        fetcher: Callable[[], Awaitable[Any]] | None = None,
        ex: int = 3600,
    ) -> Any | None:
        value = await self._client.get(key)
        if value is not None:
            return json.loads(value)
        if fetcher is None:
            return None
        result = await fetcher()
        if result is not None:
            await self._client.set(key, json.dumps(result), ex=ex)
        return result

    async def invalidate(self, key: str) -> None:
        await self._client.delete(key)


cache = Cache(settings.redis_url)

