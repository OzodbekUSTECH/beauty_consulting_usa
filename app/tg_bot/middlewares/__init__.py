from aiogram import Dispatcher

from app.tg_bot.middlewares.access_control import AccessControlMiddleware


def include_middlewares(dp: Dispatcher):
    dp.message.middleware(AccessControlMiddleware())
