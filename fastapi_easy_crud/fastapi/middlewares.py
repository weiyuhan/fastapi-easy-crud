import time
from typing import Any, Callable
from uuid import uuid4

from loguru import logger
from starlette.concurrency import iterate_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


async def log_response_body(request_id: str, url: str, response) -> Any:  # type: ignore
    response_body = [chunk async for chunk in response.body_iterator]
    response.body_iterator = iterate_in_threadpool(iter(response_body))
    logger.info(
        f"id: {request_id}, url: {url}, response_body={response_body[0].decode()}"
    )
    return response


class BasicLogMetricsMiddleWare(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Any:
        url = request.url.path
        request_id = str(uuid4())
        logger.info(f"id: {request_id}, url: {url}, request: {request.__dict__}")
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-Id"] = request_id
        logger.info(f"id: {request_id}, url: {url}, response: {response.__dict__}")
        if response.status_code >= 400:
            response = await log_response_body(
                url=url, request_id=request_id, response=response
            )
        return response
