from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.session import engine, mock_engine
from app.core.db import Base
from app.api import health_router, auth_router, amount_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup ---
    # Создаём таблицы в основной БД
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Создаём таблицы в mock БД (только для AmountORM и TransactionORM)
    from app.core.db import AmountORM, TransactionORM
    
    def create_mock_tables(sync_conn):
        """Создаёт таблицы для mock моделей в синхронном контексте"""
        AmountORM.__table__.create(sync_conn, checkfirst=True)
        TransactionORM.__table__.create(sync_conn, checkfirst=True)
    
    # Создаём таблицы напрямую в mock БД
    async with mock_engine.begin() as conn:
        await conn.run_sync(create_mock_tables)

    yield

    # --- shutdown ---
    # если нужно, тут можно сделать await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(title="Backend", lifespan=lifespan, redirect_slashes=False)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:4200"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(amount_router)

    return app


app = create_app()
