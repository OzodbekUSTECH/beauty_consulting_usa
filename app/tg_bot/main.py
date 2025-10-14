import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.di import container
from app.tg_bot.middlewares import include_middlewares
from app.tg_bot.routers import include_routers
from dishka.integrations.aiogram import setup_dishka


async def start_tg_bot():
    logging.basicConfig(level=logging.INFO)
    bot = await container.get(Bot)
    dp = await container.get(Dispatcher)
    include_middlewares(dp)
    include_routers(dp)
    setup_dishka(container, dp, auto_inject=True)

    try:
        await dp.start_polling(bot)
    finally:
        await container.close()
        await bot.session.close()

