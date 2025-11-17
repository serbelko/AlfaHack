from contextlib import asynccontextmanager
import asyncio
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy import text

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

# Флаг для автоматического запуска seed скриптов
AUTO_SEED = os.getenv("AUTO_SEED", "true").lower() == "true"


async def wait_for_db(engine_instance, db_name: str, max_retries: int = 30, delay: float = 2.0):
    """Ожидает готовности БД с повторными попытками"""
    for attempt in range(max_retries):
        try:
            async with engine_instance.begin() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info(f"{db_name} database is ready")
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"{db_name} database not ready yet (attempt {attempt + 1}/{max_retries}): {e}")
                await asyncio.sleep(delay)
            else:
                logger.error(f"{db_name} database failed to become ready after {max_retries} attempts")
                raise
    return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup ---
    logger.info("Application startup: initializing database tables")
    
    # Ждём готовности основной БД
    await wait_for_db(engine, "Main")
    
    # Создаём таблицы в основной БД
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Main database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create main database tables: {e}", exc_info=True)
        raise
    
    # Ждём готовности mock БД
    await wait_for_db(mock_engine, "Mock")
    
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

    # Автоматический запуск seed скриптов (если включено)
    if AUTO_SEED:
        try:
            logger.info("Running seed scripts...")
            
            # Запускаем seed_users
            from app.scripts.seed_users import main as seed_users_main
            await seed_users_main()
            logger.info("Seed users completed")
            
            # Запускаем seed_amounts
            from app.scripts.seed_amounts import main as seed_amounts_main
            await seed_amounts_main()
            logger.info("Seed amounts completed")
            
        except Exception as e:
            logger.warning(f"Seed scripts failed (non-critical): {e}", exc_info=True)
            # Не прерываем запуск приложения, если seed скрипты упали
    else:
        logger.info("Auto-seed disabled (set AUTO_SEED=true to enable)")

    logger.info("Application startup completed")

    yield

    # --- shutdown ---
    logger.info("Application shutdown: closing database connections")
    # если нужно, тут можно сделать await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Backend",
        lifespan=lifespan,
        redirect_slashes=False,
    )

    # Добавляем middleware для логирования (должен быть первым)
    app.add_middleware(LoggingMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",  # Vite dev server
            "http://localhost:80",
            "http://localhost:8001",    # Production frontend
            "http://localhost",       # localhost without port
            "http://127.0.0.1:5173",  # Vite dev server (IP)
            "http://127.0.0.1:80",    # Production frontend (IP)
            "http://127.0.0.1",
            "http://127.0.0.1:8001",    # AI Service (IP)
            "http://frontend:80",     # Docker network
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
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
