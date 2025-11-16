from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import settings
from collections.abc import AsyncGenerator

# Основная БД
engine = create_async_engine(
    settings.ASYNC_DATABASE_URL_computed,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False,  
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Mock БД (отдельная БД для mock-service)
mock_engine = create_async_engine(
    settings.MOCK_ASYNC_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False,
)

MockAsyncSessionLocal = async_sessionmaker(
    bind=mock_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

async def get_mock_session() -> AsyncGenerator[AsyncSession, None]:
    async with MockAsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()