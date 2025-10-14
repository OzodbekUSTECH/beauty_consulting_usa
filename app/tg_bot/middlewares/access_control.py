from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Awaitable, Dict, Any

from app.core.config import settings


class AccessControlMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user_id = str(event.from_user.id)
        allowed = settings.ALLOWED_USER_IDS

        # Если "*" в списке — доступ всем разрешён
        if "*" in allowed or user_id in allowed:
            return await handler(event, data)

        # Иначе — отказ
        return

