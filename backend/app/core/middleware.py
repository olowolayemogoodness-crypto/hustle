import time
from fastapi import Request
from app.core.logging import get_logger

logger = get_logger(__name__)


async def request_timing_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    response.headers["X-Response-Time-ms"] = f"{elapsed_ms:.2f}"
    logger.info(
        "%s %s %s %.2fms",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response
