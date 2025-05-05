import asyncio
import json
import redis.asyncio as redis
from typing import Optional


class RedisController:
    def __init__(self, host: str = "localhost", port: int = 6379, channel: str = "abc"):
        self.redis = redis.Redis(host=host, port=port, decode_responses=True)
        self.channel = channel
        self.listener_task: Optional[asyncio.Task] = None

    async def start_listener(self):
        if self.listener_task is None:
            self.listener_task = asyncio.create_task(self._listen_to_channel())

    async def _listen_to_channel(self):
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(self.channel)

        async for message in pubsub.listen():
            if message["type"] != "message":
                continue

            try:
                payload = json.loads(message["data"])  # Expects: {"klucz": "...", "json": "..."}
                key = payload["klucz"]
                json_value = payload["json"]

                await self.redis.set(key, json_value)
                print(f"[RedisController] Zapisano: {key}")

            except (json.JSONDecodeError, KeyError) as e:
                print(f"[RedisController] Błąd danych wejściowych: {e}")
            except Exception as e:
                print(f"[RedisController] Błąd ogólny: {e}")
