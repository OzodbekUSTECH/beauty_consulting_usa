from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import time
import logging

from app.core.config import settings
from app.middlewares.error_handler import handle_error

logger = logging.getLogger("app.MIDDLEWARES")


def register_middlewares(app: FastAPI, slow_threshold: float = 1.0):
    """
    Middleware, логирующий все HTTP-запросы.
    Если запрос обрабатывается дольше `slow_threshold` секунд, логируется как 'SLOWED REQUEST'.
    """

    @app.middleware("http")
    async def custom_logging(request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        processing_time = time.time() - start_time
        client = f"{request.client.host}:{request.client.port}"
        method = request.method
        path = request.url.path
        status_code = response.status_code

        if processing_time > slow_threshold:
            logger.warning(
                "SLOWED REQUEST | client=%s | method=%s | path=%s | status=%d | time=%.3fs",
                client, method, path, status_code, processing_time
            )
        else:
            logger.info(
                "REQUEST | client=%s | method=%s | path=%s | status=%d | time=%.3fs",
                client, method, path, status_code, processing_time
            )

        return response

    @app.middleware("http")
    async def error_handling_middleware(request: Request, call_next):
        return await handle_error(request, call_next)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )