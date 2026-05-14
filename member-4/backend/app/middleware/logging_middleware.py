import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logger import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log incoming request
        logger.info(f"REQUEST  {request.method} {request.url.path}")

        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(f"UNHANDLED EXCEPTION: {e}")
            raise

        process_time = (time.time() - start_time) * 1000
        logger.info(
            f"RESPONSE {request.method} {request.url.path} "
            f"status={response.status_code} time={process_time:.2f}ms"
        )

        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        return response
