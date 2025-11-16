from enum import Enum

import httpx

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class AISegment(str, Enum):
    FIN = "FIN"
    MRKT = "MRKT"


class AIService:
    def __init__(self) -> None:
        # Из настроек проекта
        self._url = settings.OLLAMA_URL.rstrip("/")

    async def classify_prompt(self, prompt: str) -> AISegment:
        """
        Классифицирует текст запроса в FIN или MRKT.

        Если что-то ломается (таймаут, неправильный JSON и т.п.) - возвращаем
        безопасный дефолт (MRKT), чтобы фронт мог показать шаблон.
        """

        classification_prompt = """
        ROLE: Ты - алгоритм классификации. Ты не даешь ответов на вопросы, а только классифицируешь их.
        TASK: Проанализируй текст после "INPUT:" и верни ровно один из двух тегов: `[FIN]` или `[MRKT]`.
        CRITERIA:
        - `[FIN]` (Finance): Вопросы о внутренних денежных потоках, бюджете, прибыли, затратах, отчетности компании.
        - `[MRKT]` (Market): Вопросы о конкурентах, доле рынка, трендах, потребителях, спросе.
        INSTRUCTION: Не приветствуй, не извиняйся, не объясняй свой выбор. Только тег.
        OUTPUT_FORMAT: [FIN] или [MRKT]

        INPUT: {prompt}
        """.format(prompt=prompt)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.OLLAMA_URL,
                    json={"prompt": classification_prompt, "stream": False},
                    timeout=30.0,
                )
            response.raise_for_status()
        except Exception as exc:
            logger.error("AI classification request failed: %r", exc, exc_info=True)
            # Фоллбек - маркетинговый шаблон
            return AISegment.MRKT

        try:
            data = response.json()
        except Exception as exc:
            logger.error("AI classification invalid JSON: %r", exc, exc_info=True)
            return AISegment.MRKT

        raw = str(data.get("message", "")).strip()
        # Поддерживаем оба варианта: [FIN] и FIN
        if raw in ("[FIN]", "FIN"):
            return AISegment.FIN
        if raw in ("[MRKT]", "MRKT"):
            return AISegment.MRKT

        logger.warning("Unexpected AI tag: %r, fallback to MRKT", raw)
        return AISegment.MRKT
