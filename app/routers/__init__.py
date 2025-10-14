from fastapi import FastAPI
from app.routers.ai import router as ai_router
from app.routers.users import router as users_router

all_routers = [
    ai_router,
    users_router,
]


def register_routers(app: FastAPI, prefix: str = ""):
    """
    Initialize all routers in the app.
    """
    for router in all_routers:
        app.include_router(router, prefix=prefix)