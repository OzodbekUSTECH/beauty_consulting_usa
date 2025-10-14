import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from dishka.integrations.fastapi import setup_dishka

from app.tg_client import tg_client
from app.core.config import settings, configure_logging
from app.di import container
from app.middlewares import register_middlewares
from app.routers import register_routers
from app.tg_client.pubsub_listener import pubsub_listener
from app.utils.dependencies import get_current_user_for_docs
from app.tg_bot.main import start_tg_bot
from app.utils.ai_state import AIAssistantStateService

configure_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    tg_bot_task = asyncio.create_task(start_tg_bot())
    tg_client_task = asyncio.create_task(tg_client.start())
    asyncio.create_task(pubsub_listener())
    ai_assistant_state_service = await container.get(AIAssistantStateService)
    await ai_assistant_state_service.set_state(False)
    yield
    tg_client_task.cancel()
    tg_bot_task.cancel()
    await app.state.dishka_container.close()
    

def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan,
                  docs_url=None,
                  redoc_url=None,
                  openapi_url=None,
                  )
    setup_dishka(container, app)

    register_middlewares(app)
    register_routers(app, settings.API_PREFIX)

    return app


app = create_app()


@app.get("/api/docs", include_in_schema=False, dependencies=[Depends(get_current_user_for_docs)])
async def custom_swagger_ui():
    return get_swagger_ui_html(
        openapi_url="/api/openapi.json",
        title="MINZIFA AI ASSISTANT",
        swagger_ui_parameters={"docExpansion": "none"},
    )

@app.get("/api/openapi.json", include_in_schema=False, dependencies=[Depends(get_current_user_for_docs)])
async def get_open_api_endpoint():
    openapi_schema = get_openapi(title="MINZIFA AI ASSISTANT", version="1.0.0", routes=app.routes)
    openapi_schema["servers"] = [
        {"url": "/", "description": "Base Path for API"},
    ]
    return openapi_schema



