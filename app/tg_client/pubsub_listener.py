from datetime import datetime, timedelta
from app.core.config import settings
from app.di import container
from app.dto.users import UpdateUserRequest
from app.interactors.users.update import UpdateUserInteractor
from app.tg_client import tg_client
from app.utils.redis_service import RedisService
from app.tg_client.handlers.ai import get_ai_response
from app.dto.ai import CreatePromptRequest
from pyrogram.enums import ParseMode, ChatAction
import logging

logger = logging.getLogger("app.tg_client.pubsub_listener")

async def process_user_queue(redis_service: RedisService, tg_id: str):
    try:
        logger.info("Начало обработки очереди сообщений для пользователя %s", tg_id)
        messages = await redis_service.get_all_messages(tg_id)
        if not messages:
            logger.info("Очередь пуста для пользователя %s", tg_id)
            return

        six_hours_ago = datetime.now() - timedelta(hours=settings.MESSAGE_EXPIRATION_HOURS)
        logger.info("Текущее время: %s", datetime.now().isoformat())
        logger.info("Граница истечения: %s (сообщения до этого времени считаются протухшими)",
                    six_hours_ago.isoformat())

        combined_prompts = []
        user_data = None

        for msg in messages:
            prompt_data = CreatePromptRequest.model_validate_json(msg)

            logger.info("Сообщение от пользователя %s создано в %s", tg_id, prompt_data.created_at.isoformat())

            if prompt_data.created_at < six_hours_ago:
                logger.warning(
                    "Обнаружено протухшее сообщение для пользователя %s (created_at: %s < expiration: %s), помечаем как неактивного",
                    tg_id,
                    prompt_data.created_at.isoformat(),
                    six_hours_ago.isoformat()
                )
                async with container() as con:
                    await redis_service.clear_queue(tg_id)
                    update_user_interactor = await con.get(UpdateUserInteractor)
                    await update_user_interactor.execute(UpdateUserRequest(tg_id=tg_id, is_active=False))
                    return

            if user_data is None:
                user_data = {
                    "tg_id": prompt_data.tg_id,
                    "username": prompt_data.username,
                    "name": prompt_data.name,
                    "phone_number": prompt_data.phone_number,
                }

            combined_prompts.append(prompt_data.prompt)

        if not combined_prompts:
            logger.info("Нет валидных сообщений для пользователя %s", tg_id)
            return

        combined = "\n\n".join(combined_prompts)
        await redis_service.clear_queue(tg_id)
        logger.info("Очищена очередь сообщений для пользователя %s", tg_id)

        request_data = CreatePromptRequest(
            tg_id=tg_id,
            prompt=combined,
            username=user_data.get("username"),
            name=user_data.get("name"),
            phone_number=user_data.get("phone_number"),
        )

        response = await get_ai_response(request_data)
        if response:
            logger.info("Отправляем ответ пользователю %s", tg_id)
            await tg_client.send_chat_action(tg_id, ChatAction.TYPING)
            await tg_client.read_chat_history(tg_id)
            await tg_client.send_message(tg_id, response, parse_mode=ParseMode.MARKDOWN)
        else:
            logger.info("Ответ от AI пустой для пользователя %s", tg_id)

    except Exception as e:
        logger.exception("Ошибка при обработке очереди для пользователя %s: %s", tg_id, str(e))


async def process_pending_queues(redis_service: RedisService):
    keys = await redis_service.redis.keys("queue:*")
    logger.info("Обнаружено %d отложенных очередей", len(keys))
    for key in keys:
        tg_id = key.decode().split(":")[1] if isinstance(key, bytes) else key.split(":")[1]
        await process_user_queue(redis_service, tg_id)


async def pubsub_listener():
    print("pubsub_listener: Запуск слушателя pubsub")
    redis_service = await container.get(RedisService)
    redis = redis_service.redis

    logger.info("Обработка отложенных сообщений при старте")
    print("pubsub_listener: Обработка отложенных сообщений при старте")
    await process_pending_queues(redis_service)

    pubsub = redis.pubsub()
    print("pubsub_listener: Создан pubsub")
    await pubsub.psubscribe(f"__keyevent@{settings.REDIS_DB}__:expired")
    print("pubsub_listener: Подписка на '__keyevent@{settings.REDIS_DB}__:expired' выполнена")

    logger.info("Подписка на события истечения TTL Redis включена")
    print("pubsub_listener: Подписка на события истечения TTL Redis включена")

    async for msg in pubsub.listen():
        print(f"pubsub_listener: Получено сообщение из pubsub: {msg}")
        if msg["type"] != "pmessage":
            continue
        key = msg.get("data", "").decode() if isinstance(msg.get("data"), bytes) else msg.get("data")
        print(f"pubsub_listener: Проверка ключа из сообщения: {key}")
        if key and key.startswith("delay_trigger:"):
            tg_id = key.split(":")[1]
            logger.info("Получено событие истечения TTL для пользователя %s", tg_id)
            print(f"pubsub_listener: Получено событие истечения TTL для пользователя {tg_id}")
            await process_user_queue(redis_service, tg_id)
