import logging
import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

from time import perf_counter

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.category import router as category_router
from app.api.routers.task import router as task_router
from app.core.logging import configure_logging

configure_logging()
logger = logging.getLogger('app.middleware')

counter_lock = threading.Lock()

app = FastAPI()
app.state.request_counter = 0

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.middleware('http')
async def log_requests(request: Request, call_next: Callable) -> Response:

    with counter_lock:
        app.state.request_counter += 1
        current_count = app.state.request_counter

    started_at = perf_counter()
    try:
        response: Response = await call_next(request)
    except Exception:
        duration_ms = (perf_counter() - started_at) * 1000
        logger.exception(
            '[#%s] Request failed: %s %s completed_in=%.2fms',
            current_count,
            request.method,
            request.url.path,
            duration_ms,
        )
        raise

    duration_ms = (perf_counter() - started_at) * 1000
    logger.info(
        '[#%s] %s %s -> %s (%.2f ms)',
        current_count,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )

    response.headers['X-Request-Number'] = str(current_count)
    return response


app.include_router(task_router, tags=['tasks'])
app.include_router(category_router, tags=['categories'])
