from pyrogram import Client, filters
from app.core.config import settings
from pyrogram.types import Message

from app.di import container
from app.dto.ai import CreatePromptRequest
from app.utils.redis_service import RedisService
from app.utils.ai_state import AIAssistantStateService

tg_client = Client(settings.SESSION_NAME, api_id=settings.API_ID, api_hash=settings.API_HASH,
             phone_number=settings.PHONE_NUMBER, session_string=settings.STRING_SESSION)


@tg_client.on_message(filters.private & filters.incoming & filters.text)
async def handle_message(client: Client, message: Message):
    print("Получено новое сообщение в Telegram")
    async with container() as con:
        redis_service = await con.get(RedisService)
        print("RedisService получен из контейнера")
        ai_assistant_state_service = await con.get(AIAssistantStateService)
        print("AIAssistantStateService получен из контейнера")
        if not await ai_assistant_state_service.get_state():
            return

        tg_id = str(message.from_user.id)
        print(f"ID пользователя: {tg_id}")
        # Создаем объект запроса
        data = CreatePromptRequest(
            tg_id=tg_id,
            username=message.from_user.username,
            name=f"{message.from_user.first_name} {message.from_user.last_name}",
            phone_number=message.from_user.phone_number,
            prompt=message.text,
        )
        print("Создан CreatePromptRequest")

        # Добавляем в очередь
        await redis_service.enqueue_message(tg_id, data)
        print("Сообщение добавлено в очередь Redis")

        # Устанавливаем триггер (заново)
        await redis_service.set_delay_trigger(tg_id, ttl=settings.TTL)
        print(f"Установлен триггер задержки для пользователя {tg_id}")

