import asyncio
import json
import logging
from typing import Any

import httpx
from fastapi import Request
from fastapi.responses import Response, StreamingResponse

from src.utils import parse_model_response
from .config import API_BASE_URL, OLLAMA_URL, SERVICE_API_TOKEN
from .schemas import PromptRequest
from .services.competitor_analyzer import analyze_competitors_streaming

from ollama import Client

ollama_client = Client(host=OLLAMA_URL)
logger = logging.getLogger(__name__)


async def get_ai_message_mock(payload: PromptRequest):
    async def stream_generator():
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=10.0)) as client:
            async with client.stream(
                "POST",
                f"{OLLAMA_URL.rstrip('/')}/api/chat",
                json={
                    "model": "bambucha/saiga-llama3",
                    "messages": [{"role": "user", "content": "Поздоровайся максимально вежливо и попроси пользователя ввести запрос"}],
                    "stream": True,
                },
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        chunk = json.loads(line)
                        message = chunk.get("message", {})
                        content = message.get("content")
                        if content:
                            yield content
                            await asyncio.sleep(0)
                    except json.JSONDecodeError as exc:
                        logger.debug("JSON decode error: %s", exc)
                        continue

    return StreamingResponse(
        stream_generator(),
        media_type="text/plain; charset=utf-8",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Pragma": "no-cache",
            "Expires": "0",
            "Transfer-Encoding": "chunked",
        },
    )


async def fetch_api_data(endpoints: list[str], authorization_header: str | None = None) -> list[dict[str, Any]]:
    if not endpoints:
        return []

    headers = {}

    if authorization_header:
        headers["Authorization"] = authorization_header

    async with httpx.AsyncClient() as api_client:
        async def fetch_endpoint(endpoint: str):
            try:
                response = await api_client.get(
                    f"{API_BASE_URL}{endpoint}",
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return {"endpoint": endpoint, "data": response.json(), "success": True}
            except Exception as exc:
d                return {"endpoint": endpoint, "error": str(exc), "success": False}

        results = await asyncio.gather(*(fetch_endpoint(endpoint) for endpoint in endpoints))

    aggregated: list[dict[str, Any]] = []
    for result in results:
        if result["success"]:
            aggregated.append({"endpoint": result["endpoint"], "data": result["data"]})
        else:
            aggregated.append({"endpoint": result["endpoint"], "error": result["error"]})
    return aggregated


async def receive_final_prompt(all_api_data: list[dict[str, Any]], user_prompt: str) -> StreamingResponse:
    final_prompt = f"""
    Пользователь задал вопрос: {user_prompt}

    Для ответа на этот вопрос были выполнены следующие запросы к API:
    {json.dumps(all_api_data, ensure_ascii=False, indent=2)}

    Проанализируй все полученные данные и дай развернутый ответ на вопрос пользователя.
    Если в некоторых запросах были ошибки, учти это при формировании ответа.
    """

    async def stream_generator():
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=10.0)) as client:
            async with client.stream(
                "POST",
                f"{OLLAMA_URL.rstrip('/')}/api/chat",
                json={
                    "model": "bambucha/saiga-llama3",
                    "messages": [{"role": "user", "content": final_prompt}],
                    "stream": True,
                },
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        chunk = json.loads(line)
                        message = chunk.get("message", {})
                        content = message.get("content")
                        if content:
                            yield content
                            await asyncio.sleep(0)
                    except json.JSONDecodeError as exc:
                        logger.debug("JSON decode error: %s", exc)
                        continue

    return StreamingResponse(
        stream_generator(),
        media_type="text/plain; charset=utf-8",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Pragma": "no-cache",
            "Expires": "0",
            "Transfer-Encoding": "chunked",
        },
    )


async def get_requests(payload: PromptRequest) -> dict[str, list[str]] | Response:
    system_prompt = f"""
        Ты - интеллектуальный агент, который помогает пользователю, взаимодействуя с внешним API.
        Твоя задача - анализировать запрос пользователя и решать, какие эндпоинты вызвать.

        Доступные эндпоинты:
        1. GET /api/amount/ - данные по счету (name, count)
        2. GET /api/amount/transaction - данные об одной транзакции (amount_id, created_at, type, category, count)
        3. GET /api/amount/history - история транзакций (amount_id, created_at, type, category, count)

        Эндпоинт history поддерживает параметры amount_id, from_date, to_date, type, category, count.
        Пример: /api/amount/history?amount_id=1&from_date=2024-01-01&to_date=2024-01-31&type=income

        Верни JSON строго в формате:
        {{
            "endpoints": ["/здесь_нужный_эндпоинт1", "/здесь_нужный_эндпоинт2", ...]
        }}

        Если вызов API не требуется, ответь как обычный помощник.

        Текущий запрос пользователя: {payload.prompt}
    """

    async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=10.0)) as client:
        try:
            response = await client.post(
                f"{OLLAMA_URL.rstrip('/')}/api/generate",
                json={
                    "model": "bambucha/saiga-llama3",
                    "prompt": system_prompt,
                    "stream": False,
                },
            )
            response.raise_for_status()
            response_data = response.json()

            action_data = parse_model_response(response_data.get("response", ""))
            if action_data:
                return action_data

            return Response(status_code=200, content=response_data.get("response", ""))
        except httpx.ReadTimeout:
            return Response(status_code=504, content="Таймаут при запросе к модели. Попробуйте позже.")
        except httpx.HTTPError as exc:
            return Response(status_code=500, content=f"Ошибка при запросе к модели: {str(exc)}")


async def get_ai_message(payload: PromptRequest, request: Request) -> Response | StreamingResponse:
    """
    Обрабатывает пользовательский запрос: классифицирует его и запускает соответствующий сценарий.
    """
    logger.info("📥 Получен запрос на классификацию: '%s...'", payload.prompt[:100])
    
    # Принимаем заголовок Authorization как есть
    authorization_header = request.headers.get("Authorization")

    classification_prompt = f"""
        ROLE: Ты — алгоритм классификации. Ты не даешь ответов на вопросы, а только классифицируешь их.
        TASK: Проанализируй текст после "INPUT:" и верни ровно один из двух тегов: `[FIN]` или `[MRKT]`.
        CRITERIA:
        - `[FIN]` (Finance): Вопросы о денежных потоках, бюджете, прибыли, затратах, отчетности компании.
        - `[MRKT]` (Market): Вопросы о конкурентах, доле рынка, трендах, потребителях, спросе.
        OUTPUT_FORMAT: [FIN] или [MRKT]

        INPUT: {payload.prompt}
    """

    async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=10.0)) as client:
        try:
            response = await client.post(
                f"{OLLAMA_URL.rstrip('/')}/api/generate",
                json={
                    "model": "bambucha/saiga-llama3",
                    "prompt": classification_prompt,
                    "stream": False,
                },
            )
            response.raise_for_status()

            classification_result = response.json().get("response", "").strip()
            logger.info("✅ Категория определена: %s", classification_result)

            if classification_result == "[FIN]":
                requests_data = await get_requests(payload)
                if isinstance(requests_data, Response):
                    return requests_data
                endpoints = requests_data.get("endpoints", [])
                api_data = await fetch_api_data(endpoints, authorization_header=authorization_header)
                return await receive_final_prompt(api_data, payload.prompt)

            if classification_result == "[MRKT]":
                return await analyze_competitors(payload)

            logger.warning("⚠️ Неизвестный результат классификации: %s", classification_result)
            return Response(status_code=400, content=f"Не удалось определить категорию запроса: {classification_result}")
        except httpx.ReadTimeout:
            logger.error("⏱️ Таймаут при классификации запроса")
            return Response(status_code=504, content="Таймаут при классификации запроса. Попробуйте позже.")
        except httpx.HTTPError as exc:
            logger.error("❌ Ошибка при классификации запроса: %s", exc)
            return Response(status_code=500, content=f"Ошибка при классификации запроса: {str(exc)}")


async def analyze_competitors(payload: PromptRequest) -> StreamingResponse:
    """
    Запускает streaming-анализ конкурентов.
    """
    logger.info("📥 Получен запрос на анализ конкурентов: '%s...'", payload.prompt[:100])

    async def generate():
        try:
            async for chunk in analyze_competitors_streaming(payload.prompt):
                yield chunk
                await asyncio.sleep(0)
        except Exception as exc:
            logger.error("❌ Критическая ошибка при анализе: %s", exc, exc_info=True)
            yield f"\n\n❌ Ошибка при анализе: {str(exc)}\n"

    return StreamingResponse(
        generate(),
        media_type="text/plain; charset=utf-8",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Pragma": "no-cache",
            "Expires": "0",
            "Transfer-Encoding": "chunked",
        },
    )

