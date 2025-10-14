from aiogram import Dispatcher
from app.tg_bot.routers.welcome import router as welcome_router
from app.tg_bot.routers.assistant_panel import router as assistant_panel_router
from app.tg_bot.routers.users_panel import router as users_panel_router

routers = [welcome_router, assistant_panel_router, users_panel_router]

def include_routers(dp: Dispatcher) -> None:
    for router in routers:
        dp.include_router(router)
