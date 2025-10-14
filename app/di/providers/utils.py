from aiogram import Bot, Dispatcher
from dishka import Provider, Scope, provide
from openai import AsyncOpenAI
from redis.asyncio import Redis

from app.core.config import settings
from app.utils.ai_state import AIAssistantStateService
from app.utils.redis_service import RedisService


class UtilsProvider(Provider):
    
    scope = Scope.APP
    
    
    assistant_state = provide(AIAssistantStateService)


    @provide(scope=Scope.APP)
    def provide_openai_client(self) -> AsyncOpenAI:
        return AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
        )


    @provide(scope=Scope.APP)
    def provide_aiogram_bot(self) -> Bot:
        return Bot(
            token=settings.BOT_TOKEN,
        )
        
    @provide(scope=Scope.APP)
    def provide_aiogram_dispatcher(self) -> Dispatcher:
        return Dispatcher()


    @provide(scope=Scope.APP)
    async def provide_redis(self) -> RedisService:
        redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        # Важно: Установим notify-keyspace-events Ex для поддержки событий expired
        await redis_client.config_set('notify-keyspace-events', 'Ex')
        return RedisService(redis_client)
