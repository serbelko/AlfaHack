"""
Middleware для логирования HTTP запросов.
"""
import time
import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.logger import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware для логирования всех HTTP запросов и ответов.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Обрабатывает запрос и логирует информацию о нём.
        """
        start_time = time.time()

        # Логируем входящий запрос
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        query_params = str(request.query_params) if request.query_params else ""

        logger.info(
            f"Request started: {method} {path}"
            + (f"?{query_params}" if query_params else "")
            + f" from {client_ip}"
        )

        # Обрабатываем запрос
        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            # Логируем успешный ответ
            logger.info(
                f"Request completed: {method} {path} - "
                f"Status: {response.status_code} - "
                f"Time: {process_time:.3f}s"
            )

            return response

        except Exception as e:
            process_time = time.time() - start_time

            # Логируем ошибку
            logger.error(
                f"Request failed: {method} {path} - "
                f"Error: {str(e)} - "
                f"Time: {process_time:.3f}s",
                exc_info=True,
            )
            raise

