import json
import asyncio
from src.utils import parse_model_response
import httpx
<<<<<<< Updated upstream
import logging
from fastapi.responses import StreamingResponse
from .config import OLLAMA_URL
=======
from fastapi.responses import Response, StreamingResponse
from .config import OLLAMA_URL, API_BASE_URL
>>>>>>> Stashed changes
from .schemas import PromptRequest
from .services.competitor_analyzer import analyze_competitors_streaming

from ollama import Client
ollama_client = Client(
  host=OLLAMA_URL,
)

<<<<<<< Updated upstream
logger = logging.getLogger(__name__)
=======
async def generate_stream_generator(response: httpx.Response) -> str:
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

async def responce_stream(response: httpx.Response) -> StreamingResponse:
    return StreamingResponse(
        generate_stream_generator(response),
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
>>>>>>> Stashed changes

async def get_ai_message_mock(payload: PromptRequest):
    async def stream_generator():
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=10.0)) as client:
            async with client.stream(
                "POST",
                f"{OLLAMA_URL.rstrip('/')}/api/chat",
                json={
                    "model": "bambucha/saiga-llama3",
                    "messages": [{"role": "user", "content": "Поздоровайся максимально вежливо и попроси пользователя ввести запрос"}],
                    "stream": True
                }
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
                                    await asyncio.sleep(0)
                        except json.JSONDecodeError as e:
                            print(f"JSON decode error: {e}, line: {line[:100]}")
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
            "Transfer-Encoding": "chunked"
        }
    )
    


async def fetch_api_data(endpoints: list[str]) -> list[dict]:
    """
    Выполняет параллельные запросы к нескольким API endpoints.
    
    Args:
        endpoints: Список endpoints для запросов
        
    Returns:
        Список данных из API
    """
    if not isinstance(endpoints, list) or len(endpoints) == 0:
        return []
    
    # Делаем параллельные запросы ко всем endpoints
    async with httpx.AsyncClient() as api_client:
        # Создаем задачи для всех запросов
        async def fetch_endpoint(endpoint: str):
            """Выполняет запрос к одному endpoint"""
            try:
                response = await api_client.get(
                    f"{API_BASE_URL}{endpoint}",
                    timeout=30.0
                )
                response.raise_for_status()
                return {"endpoint": endpoint, "data": response.json(), "success": True}
            except Exception as e:
                return {"endpoint": endpoint, "error": str(e), "success": False}
        
        # Выполняем все запросы параллельно
        tasks = [fetch_endpoint(endpoint) for endpoint in endpoints]
        results = await asyncio.gather(*tasks)
        
        # Формируем структурированные данные из всех запросов
        all_api_data = []
        for result in results:
            if result["success"]:
                all_api_data.append({
                    "endpoint": result["endpoint"],
                    "data": result["data"]
                })
            else:
                all_api_data.append({
                    "endpoint": result["endpoint"],
                    "error": result["error"]
                })

        return all_api_data

async def receive_final_prompt(all_api_data: list[dict], user_prompt: str) -> StreamingResponse:
    """
    Формирует финальный промпт с данными из API и отправляет его в модель для получения ответа.
    
    Args:
        all_api_data: Данные из всех API запросов
        user_prompt: Исходный вопрос пользователя
        
    Returns:
        StreamingResponse с ответом от модели
    """
    # Формируем промпт с данными из всех API запросов и передаем обратно в модель
    final_prompt = f"""
    Пользователь задал вопрос: {user_prompt}
    
    Для ответа на этот вопрос были выполнены следующие запросы к API:
    {json.dumps(all_api_data, ensure_ascii=False, indent=2)}
    
    Проанализируй все полученные данные и дай развернутый ответ на вопрос пользователя на основе полученной информации.
    Если в некоторых запросах были ошибки, учти это при формировании ответа.
    """
    
    # Создаем генератор, который сам управляет контекстом стрима
    async def stream_generator():
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=10.0)) as client:
            async with client.stream(
                "POST",
                f"{OLLAMA_URL.rstrip('/')}/api/chat",
                json={
                    "model": "bambucha/saiga-llama3",
                    "messages": [{"role": "user", "content": final_prompt}],
                    "stream": True
                }
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
                                    await asyncio.sleep(0)
                        except json.JSONDecodeError as e:
                            print(f"JSON decode error: {e}, line: {line[:100]}")
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
            "Transfer-Encoding": "chunked"
        }
    )


<<<<<<< Updated upstream
async def get_ai_message(payload: PromptRequest):
=======

async def get_requests(payload: PromptRequest) -> str:
    system_prompt = f"""
        Ты - интеллектуальный агент, который помогает пользователю, взаимодействуя с внешним API.
        Твоя задача - анализировать запрос пользователя и решать, по каким методам обратиться к API.

        Доступные эндпоинты микросервиса:
        1. GET /api/amount/ - данные по счету
        Поля: name, count
        2. GET /api/amount/transaction - данные об одной транзакции
        Поля: amount_id, created_at, type, category, count
        3. GET /api/amount/history - история транзакций
        Поля: amount_id, created_at, type, category, count

        эндпоинт history имеет параметры: amount_id, from_date, to_date, type, category, count
        По ним можно фильтровать данные так: 
        /api/amount/history?amount_id=1&from_date=2024-01-01&to_date=2024-01-31&type=income&category=salary

        Если для ответа на вопрос пользователя требуется вызов API, ты ДОЛЖЕН вернуть ответ в строго следующем JSON-формате:
        {{
            "endpoints": ["/здесь_нужный_эндпоинт1", "/здесь_нужный_эндпоинт2", ...]
        }}
        
        Если нужен только один endpoint, используй массив с одним элементом: {{"endpoints": ["/api/amount/"]}}
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
                    "stream": False
                }
            )
            response.raise_for_status()
            response_data = response.json()
            if action_data := parse_model_response(response_data.get("response", "")):
                return action_data
            else:
                return Response(status_code=200, content=response_data.get("response", ""))
        except httpx.ReadTimeout:
            return Response(status_code=504, content="Таймаут при запросе к модели. Попробуйте позже.")
        except httpx.HTTPError as e:
            return Response(status_code=500, content=f"Ошибка при запросе к модели: {str(e)}")





async def get_ai_message(payload: PromptRequest) -> str | StreamingResponse:
>>>>>>> Stashed changes
    """
    Обработчик для получения ответа от AI.
    Определяет категорию запроса и обрабатывает соответственно.
    
    Args:
        payload: Запрос с промптом пользователя
        
    Returns:
<<<<<<< Updated upstream
        Для MRKT - StreamingResponse с анализом конкурентов
        Для FIN - строка "FIN"
=======
        Ответ от AI модели (строка или StreamingResponse)
>>>>>>> Stashed changes
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

<<<<<<< Updated upstream
    try:
        async with httpx.AsyncClient() as client:
            logger.debug("🤖 Отправляю запрос на классификацию в AI")
=======
    async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=10.0)) as client:
        try:
>>>>>>> Stashed changes
            response = await client.post(
                f"{OLLAMA_URL.rstrip('/')}/api/generate",
                json={
                    "model": "bambucha/saiga-llama3",
                    "prompt": classification_prompt,
                    "stream": False
<<<<<<< Updated upstream
                },
                timeout=30.0
=======
                }
>>>>>>> Stashed changes
            )
            response.raise_for_status()

            response_data = response.json()
<<<<<<< Updated upstream
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
=======
            classification_result = response_data.get("response", "").strip()
            if classification_result == "[FIN]":
                requests_data = await get_requests(payload)
                api_data = await fetch_api_data(requests_data["endpoints"])
                return await receive_final_prompt(api_data, payload.prompt)

            elif classification_result == "[MRKT]":
                return "MRKT"
            else:
                return f"Неизвестный результат классификации: {classification_result}"
        except httpx.ReadTimeout:
            return "Таймаут при классификации запроса. Попробуйте позже."
        except httpx.HTTPError as e:
            return f"Ошибка при классификации запроса: {str(e)}"
>>>>>>> Stashed changes

