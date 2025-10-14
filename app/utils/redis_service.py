from redis.asyncio import Redis
from typing import List

from app.dto.ai import CreatePromptRequest


class RedisService:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    async def enqueue_message(self, tg_id: str, prompt: CreatePromptRequest):
        """Добавляет сообщение в очередь для указанного пользователя."""
        json_data = prompt.model_dump_json()  # Сериализация объекта в JSON
        print(f"enqueue_message: Добавление сообщения в очередь пользователя {tg_id}: {json_data}")
        await self.redis.rpush(f'queue:{tg_id}', json_data)

    async def get_all_messages(self, tg_id: str) -> List[str]:
        print(f"get_all_messages: Получение всех сообщений для пользователя {tg_id}")
        messages = await self.redis.lrange(f"queue:{tg_id}", 0, -1)
        print(f"get_all_messages: Найдено {len(messages)} сообщений для пользователя {tg_id}")
        return messages

    async def clear_queue(self, tg_id: str):
        print(f"clear_queue: Очистка очереди для пользователя {tg_id}")
        await self.redis.delete(f"queue:{tg_id}")

    async def set_delay_trigger(self, tg_id: str, ttl: int = 5):
        print(f"set_delay_trigger: Установка триггера задержки для пользователя {tg_id} с TTL={ttl}")
        await self.redis.set(f"delay_trigger:{tg_id}", "1", ex=ttl)
