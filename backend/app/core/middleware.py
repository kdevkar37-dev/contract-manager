from __future__ import annotations

import logging
import time
from uuid import uuid4

from fastapi import Request


logger = logging.getLogger("contract_manager.api")


async def request_logging_middleware(request: Request, call_next):
    request_id = str(uuid4())
    request.state.request_id = request_id

    start_time = time.perf_counter()

    try:
        response = await call_next(request)

        duration_ms = (time.perf_counter() - start_time) * 1000

        response.headers["X-Request-ID"] = request_id

        logger.info(
            "%s %s -> %s (%.2f ms) request_id=%s",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            request_id,
        )

        return response

    except Exception:
        duration_ms = (time.perf_counter() - start_time) * 1000

        logger.exception(
            "%s %s -> unhandled error (%.2f ms) request_id=%s",
            request.method,
            request.url.path,
            duration_ms,
            request_id,
        )

        raise