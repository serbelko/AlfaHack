from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.session import engine, mock_engine
from app.core.db import Base
from app.core.middleware import LoggingMiddleware
from app.core.logger import get_logger
from app.core.error_handlers import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)
from app.api import health_router, auth_router, amount_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup ---
    logger.info("Application startup: initializing database tables")
    
    # Создаём таблицы в основной БД
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Main database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create main database tables: {e}", exc_info=True)
        raise
    
    # Создаём таблицы в mock БД (только для AmountORM и TransactionORM)
    from app.core.db import AmountORM, TransactionORM
    
    def create_mock_tables(sync_conn):
        """Создаёт таблицы для mock моделей в синхронном контексте"""
        AmountORM.__table__.create(sync_conn, checkfirst=True)
        TransactionORM.__table__.create(sync_conn, checkfirst=True)
    
    try:
        # Создаём таблицы напрямую в mock БД
        async with mock_engine.begin() as conn:
            await conn.run_sync(create_mock_tables)
        logger.info("Mock database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create mock database tables: {e}", exc_info=True)
        raise

    logger.info("Application startup completed")

    yield

    # --- shutdown ---
    logger.info("Application shutdown: closing database connections")
    # если нужно, тут можно сделать await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(title="Backend", lifespan=lifespan, redirect_slashes=False)

    # Добавляем middleware для логирования (должен быть первым)
    app.add_middleware(LoggingMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Глобальные обработчики исключений
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(amount_router)

    logger.info("FastAPI application created and configured")
    return app


app = create_app()
