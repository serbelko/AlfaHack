"""
Сервис для работы с поисковыми системами (DuckDuckGo)
"""
import asyncio
import httpx
import logging
import time
from typing import List, Dict
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)


async def search_google_async(query: str, num_results: int = 5) -> List[str]:
    """
    Асинхронный поиск через DuckDuckGo (более надежный, чем Google)
    
    Args:
        query: Поисковый запрос
        num_results: Количество результатов
        
    Returns:
        Список URL-адресов
    """
    start_time = time.time()
    logger.info(f"🔍 Начинаю поиск через DuckDuckGo: '{query}' (запрошено результатов: {num_results})")
    
    try:
        # Запускаем синхронный поиск в отдельном потоке
        loop = asyncio.get_event_loop()
        
        def _search():
            try:
                # Используем DuckDuckGo Search
                with DDGS() as ddgs:
                    results = []
                    # Ищем результаты
                    for r in ddgs.text(query, max_results=num_results, region='ru-ru'):
                        if 'href' in r:
                            results.append(r['href'])
                        elif 'url' in r:
                            results.append(r['url'])
                    return results[:num_results]
            except Exception as e:
                logger.warning(f"⚠️ Ошибка в DuckDuckGo поиске: {e}")
                return []
        
        results = await loop.run_in_executor(None, _search)
        results = results[:num_results] if results else []
        
        elapsed = time.time() - start_time
        
        if not results:
            logger.warning(f"⚠️ Поиск не вернул результатов для '{query}' за {elapsed:.2f}с")
        else:
            logger.info(f"✅ Поиск завершен: найдено {len(results)} результатов за {elapsed:.2f}с")
        
        return results
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"❌ Ошибка при поиске за {elapsed:.2f}с: {e}", exc_info=True)
        # Возвращаем пустой список вместо исключения, чтобы процесс продолжался
        return []


async def generate_search_queries(user_request: str, ollama_url: str) -> List[str]:
    """
    Генерирует поисковые запросы для Google на основе запроса пользователя
    
    Args:
        user_request: Запрос пользователя
        ollama_url: URL для Ollama API
        
    Returns:
        Список поисковых запросов
    """
    start_time = time.time()
    logger.info(f"🤖 Генерирую поисковые запросы для: '{user_request[:100]}...'")
    
    prompt = f"""
ROLE: Ты — помощник для генерации поисковых запросов.
TASK: На основе запроса пользователя сгенерируй 3-5 конкретных поисковых запросов для анализа конкурентов.

ИНСТРУКЦИЯ:
1. Проанализируй запрос пользователя
2. Определи, какие поисковые запросы помогут найти информацию о конкурентах
3. Верни ТОЛЬКО JSON массив строк с запросами, без дополнительных объяснений
4. Запросы должны быть на русском языке
5. Запросы должны быть конкретными и релевантными

ФОРМАТ ОТВЕТА (только JSON, без markdown):
["запрос 1", "запрос 2", "запрос 3"]

ЗАПРОС ПОЛЬЗОВАТЕЛЯ: {user_request}
"""
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{ollama_url.rstrip('/')}/api/generate",
                json={
                    "model": "bambucha/saiga-llama3",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60.0
            )
            response.raise_for_status()
            
            result = response.json()
            response_text = result.get("response", "").strip()
            
            # Парсим JSON из ответа
            import json
            # Убираем markdown код блоки если есть
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1]) if len(lines) > 2 else response_text
            
            try:
                queries = json.loads(response_text)
                if isinstance(queries, list):
                    queries = queries[:5]  # Максимум 5 запросов
                else:
                    queries = [queries] if queries else []
            except json.JSONDecodeError:
                # Если не удалось распарсить JSON, пытаемся извлечь запросы из текста
                logger.warning(f"⚠️ Не удалось распарсить JSON, извлекаю запросы из текста")
                lines = [line.strip() for line in response_text.split("\n") if line.strip()]
                queries = lines[:5]
            
            elapsed = time.time() - start_time
            logger.info(f"✅ Сгенерировано {len(queries)} поисковых запросов за {elapsed:.2f}с: {queries}")
            
            return queries
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"❌ Ошибка при генерации запросов за {elapsed:.2f}с: {e}")
        raise

