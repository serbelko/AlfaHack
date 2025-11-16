from fastapi import APIRouter
from .views import get_ai_message, get_ai_message_mock

router = APIRouter(prefix="/api")


router.add_api_route("/ai/message/", get_ai_message, methods=["POST"])
router.add_api_route("/health_check/", lambda: {"status": "ok"}, methods=["GET"])
router.add_api_route("/ai/message/mock/", get_ai_message_mock, methods=["POST"])