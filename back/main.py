from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.session import engine
from app.core.db import Base
from app.api import health_router, auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup ---
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

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

    return app


app = create_app()
