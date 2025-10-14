from app.dto.ai import SetAssistantStateRequest, AssistantStateResponse
from app.utils.redis_service import RedisService


ASSISTANT_STATE_KEY = 'assistant_state_enabled'

class AIAssistantStateService:
    def __init__(self, redis_service: RedisService):
        self.redis_service = redis_service

    async def toggle_state(self) -> bool:
        current_state = await self.get_state()
        new_state = not current_state
        await self.set_state(new_state)
        return new_state

    async def get_state(self) -> bool:
        value = await self.redis_service.redis.get(ASSISTANT_STATE_KEY)
        if value is None:
            # По умолчанию включено
            return True
        value = value.decode() if isinstance(value, bytes) else str(value)
        return value == '1'

    async def set_state(self, enabled: bool) -> bool:
        await self.redis_service.redis.set(ASSISTANT_STATE_KEY, '1' if enabled else '0')
        return enabled
        