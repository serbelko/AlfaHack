import json
import asyncio
import httpx
import logging
from fastapi.responses import StreamingResponse
from .config import OLLAMA_URL
from .schemas import PromptRequest
from .services.competitor_analyzer import analyze_competitors_streaming

from ollama import Client
ollama_client = Client(
  host=OLLAMA_URL,
)

logger = logging.getLogger(__name__)

async def get_ai_message_mock(payload: PromptRequest):
    async def generate():
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{OLLAMA_URL.rstrip('/')}/api/chat",
                json={
                    "model": "bambucha/saiga-llama3",
                    "messages": [{"role": "user", "content": "Поздоровайся максимально вежливо и попроси пользователя ввести запрос"}],
                    "stream": True
                },
                timeout=30.0
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            chunk = json.loads(line)

                            if "message" in chunk and "content" in chunk["message"]:
                                content = chunk["message"]["content"]
                                if content:
                                    yield content
                                    # Небольшая задержка для обеспечения отправки чанков
                                    await asyncio.sleep(0)

                        except json.JSONDecodeError as e:
                            print(f"JSON decode error: {e}, line: {line[:100]}")
                            continue
    
    return StreamingResponse(
        generate(), 
        media_type="text/plain; charset=utf-8",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Pragma": "no-cache",
            "Expires": "0",
            "Transfer-Encoding": "chunked"
        }
    )


async def get_ai_message(payload: PromptRequest):
    """
    Обработчик для получения ответа от AI.
    Определяет категорию запроса и обрабатывает соответственно.
    
    Args:
        payload: Запрос с промптом пользователя
        
    Returns:
        Для MRKT - StreamingResponse с анализом конкурентов
        Для FIN - строка "FIN"
    """
    logger.info(f"📥 Получен запрос на классификацию: '{payload.prompt[:100]}...'")
    
    classification_prompt = """
        ROLE: Ты — алгоритм классификации. Ты не даешь ответов на вопросы, а только классифицируешь их.
        TASK: Проанализируй текст после "INPUT:" и верни ровно один из двух тегов: `[FIN]` или `[MRKT]`.
        CRITERIA:
        - `[FIN]` (Finance): Вопросы о внутренних денежных потоках, бюджете, прибыли, затратах, отчетности компании.
        - `[MRKT]` (Market): Вопросы о конкурентах, доле рынка, трендах, потребителях, спросе.
        INSTRUCTION: Не приветствуй, не извиняйся, не объясняй свой выбор. Только тег.
        OUTPUT_FORMAT: [FIN] или [MRKT]

        INPUT: {prompt}
    """.format(prompt=payload.prompt)

    try:
        async with httpx.AsyncClient() as client:
            logger.debug("🤖 Отправляю запрос на классификацию в AI")
            response = await client.post(
                f"{OLLAMA_URL.rstrip('/')}/api/generate",
                json={
                    "model": "bambucha/saiga-llama3",
                    "prompt": classification_prompt,
                    "stream": False
                },
                timeout=30.0
            )
            response.raise_for_status()

            response_data = response.json()
            category = response_data.get("response", "").strip()
            logger.info(f"✅ Категория определена: {category}")
            
            if "[MRKT]" in category or category == "MRKT":
                # Для MRKT запросов запускаем анализ конкурентов со streaming
                logger.info("🚀 Запускаю анализ конкурентов для MRKT запроса")
                return await analyze_competitors(payload)
            elif "[FIN]" in category or category == "FIN":
                # Для FIN запросов возвращаем категорию
                logger.info("✅ Запрос классифицирован как FIN")
                return {"category": "FIN", "message": "Запрос относится к категории Finance"}
            else:
                logger.warning(f"⚠️ Не удалось определить категорию. Ответ AI: {category}")
                return {"category": "UNKNOWN", "message": f"Не удалось определить категорию. Ответ AI: {category}"}
    except Exception as e:
        logger.error(f"❌ Ошибка при классификации: {e}", exc_info=True)
        return {"category": "ERROR", "message": f"Ошибка при классификации: {str(e)}"}


async def analyze_competitors(payload: PromptRequest):
    """
    Обработчик для анализа конкурентов со streaming ответом
    
    Args:
        payload: Запрос с промптом пользователя
        
    Returns:
        StreamingResponse с результатами анализа
    """
    logger.info(f"📥 Получен запрос на анализ конкурентов: '{payload.prompt[:100]}...'")
    
    async def generate():
        try:
            async for chunk in analyze_competitors_streaming(payload.prompt):
                yield chunk
                await asyncio.sleep(0)  # Небольшая задержка для обеспечения отправки чанков
        except Exception as e:
            logger.error(f"❌ Критическая ошибка при анализе: {e}", exc_info=True)
            yield f"\n\n❌ Ошибка при анализе: {str(e)}\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/plain; charset=utf-8",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Pragma": "no-cache",
            "Expires": "0",
            "Transfer-Encoding": "chunked"
        }
    )

