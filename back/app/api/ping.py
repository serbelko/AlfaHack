from fastapi import APIRouter
from app.core.logger import get_logger

router = APIRouter(
    tags=["health"],
    redirect_slashes=False
)

logger = get_logger(__name__)


@router.get("/ping", summary="Liveness probe")
async def ping():
    logger.debug("Health check ping received")
    return {"status": "ok"}