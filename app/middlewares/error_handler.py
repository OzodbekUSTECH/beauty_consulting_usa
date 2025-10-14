import logging
import traceback

from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions.app_error import AppError
from app.exceptions.messages import ErrorMessages

logger = logging.getLogger("app.middlewares.error_handler")

async def handle_error(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except AppError as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"error": e.message}
        )
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"Unhandled error: {str(e)}\nRequest URL: {request.url}\n{tb}")
        return JSONResponse(
            status_code=500,
            content={"error": ErrorMessages.INTERNAL_SERVER_ERROR}
        )
