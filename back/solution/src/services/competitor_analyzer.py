"""
Сервис для анализа конкурентов с использованием AI
"""
import asyncio
import httpx
import logging
import time
from typing import List, Dict
from ..config import (
    OLLAMA_URL, MAX_TEXT_LENGTH, MAX_SEARCH_RESULTS, 
    MAX_URLS_TO_ANALYZE, MAX_TEXT_FOR_AI, PARALLEL_PARSING
)
from .google_search import search_google_async, generate_search_queries
from .html_parser import get_text_from_url

logger = logging.getLogger(__name__)


async def analyze_competitors(user_request: str) -> Dict[str, any]:
    """
    Проводит полный анализ конкурентов:
    1. Генерирует поисковые запросы
    2. Ищет ссылки через DuckDuckGo
    3. Получает текст со страниц
    4. Анализирует через AI
    
    Args:
        user_request: Запрос пользователя
        
    Returns:
        Словарь с результатами анализа
    """
    ollama_url = OLLAMA_URL.rstrip('/')
    
    # Шаг 1: Генерируем поисковые запросы
    search_queries = await generate_search_queries(user_request, ollama_url)
    
    # Шаг 2: Ищем ссылки для каждого запроса
    all_urls = []
    for query in search_queries:
        urls = await search_google_async(query, num_results=MAX_SEARCH_RESULTS)
        all_urls.extend(urls)
    
    # Убираем дубликаты и ограничиваем количество
    unique_urls = list(dict.fromkeys(all_urls))[:MAX_URLS_TO_ANALYZE]
    
    # Шаг 3: Получаем текст со страниц (параллельно для ускорения)
    if PARALLEL_PARSING:
        tasks = [get_text_from_url(url, max_length=MAX_TEXT_LENGTH) for url in unique_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        texts = []
        for url, result in zip(unique_urls, results):
            if not isinstance(result, Exception) and result:
                text_for_ai = result[:MAX_TEXT_FOR_AI] if len(result) > MAX_TEXT_FOR_AI else result
                texts.append({"url": url, "text": text_for_ai})
    else:
        texts = []
        for url in unique_urls:
            text = await get_text_from_url(url, max_length=MAX_TEXT_LENGTH)
            if text:
                text_for_ai = text[:MAX_TEXT_FOR_AI] if len(text) > MAX_TEXT_FOR_AI else text
                texts.append({"url": url, "text": text_for_ai})
    
    # Шаг 4: Анализируем через AI (оптимизированный промпт)
    texts_for_ai = texts[:MAX_URLS_TO_ANALYZE]
    analysis_prompt = f"""Проанализируй конкурентов: {user_request}

ИНФОРМАЦИЯ:
{chr(10).join([f"• {item['url']}: {item['text']}" for item in texts_for_ai])}

Ответь кратко:
1. Ключевые конкуренты
2. Их особенности  
3. Выводы"""
    
    # Отправляем запрос в AI
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{ollama_url}/api/generate",
            json={
                "model": "bambucha/saiga-llama3",
                "prompt": analysis_prompt,
                "stream": False
            },
            timeout=120.0
        )
        response.raise_for_status()
        
        result = response.json()
        analysis = result.get("response", "Не удалось получить анализ")
    
    return {
        "search_queries": search_queries,
        "urls_found": len(unique_urls),
        "urls_analyzed": len(texts),
        "analysis": analysis
    }


async def analyze_competitors_streaming(user_request: str):
    """
    Проводит анализ конкурентов со streaming ответом
    
    Args:
        user_request: Запрос пользователя
        
    Yields:
        Части ответа для streaming
    """
    total_start_time = time.time()
    ollama_url = OLLAMA_URL.rstrip('/')
    
    logger.info(f"🚀 Начинаю анализ конкурентов для запроса: '{user_request[:100]}...'")
    
    # Шаг 1: Генерируем поисковые запросы
    step_start = time.time()
    yield "🔍 Генерирую поисковые запросы...\n\n"
    logger.info("📝 Этап 1/4: Генерация поисковых запросов")
    
    search_queries = await generate_search_queries(user_request, ollama_url)
    step_elapsed = time.time() - step_start
    yield f"✅ Найдено {len(search_queries)} запросов для поиска (заняло {step_elapsed:.1f}с)\n\n"
    logger.info(f"✅ Этап 1 завершен за {step_elapsed:.2f}с")
    
    # Шаг 2: Ищем ссылки
    step_start = time.time()
    yield "🌐 Ищу ссылки через DuckDuckGo...\n\n"
    logger.info("📝 Этап 2/4: Поиск ссылок через DuckDuckGo")
    
    all_urls = []
    for i, query in enumerate(search_queries, 1):
        yield f"  Поиск {i}/{len(search_queries)}: {query}\n"
        query_start = time.time()
        try:
            urls = await search_google_async(query, num_results=MAX_SEARCH_RESULTS)
            query_elapsed = time.time() - query_start
            all_urls.extend(urls)
            if urls:
                yield f"  ✅ Найдено {len(urls)} ссылок ({query_elapsed:.1f}с)\n"
            else:
                yield f"  ⚠️ Не найдено ссылок ({query_elapsed:.1f}с) - возможно, Google блокирует запросы\n"
        except Exception as e:
            query_elapsed = time.time() - query_start
            logger.error(f"❌ Ошибка при поиске '{query}': {e}")
            yield f"  ❌ Ошибка при поиске ({query_elapsed:.1f}с): {str(e)[:50]}\n"
    
    unique_urls = list(dict.fromkeys(all_urls))[:MAX_URLS_TO_ANALYZE]
    step_elapsed = time.time() - step_start
    yield f"\n📊 Всего уникальных ссылок: {len(unique_urls)} (будет проанализировано максимум {MAX_URLS_TO_ANALYZE}) (поиск занял {step_elapsed:.1f}с)\n\n"
    logger.info(f"✅ Этап 2 завершен за {step_elapsed:.2f}с, найдено {len(unique_urls)} ссылок")
    
    # Если не найдено ссылок, предупреждаем пользователя
    if not unique_urls:
        yield "⚠️ ВНИМАНИЕ: Не удалось найти ссылки через DuckDuckGo.\n"
        yield "Возможные причины:\n"
        yield "  • Проблемы с сетью или подключением\n"
        yield "  • Запрос не вернул результатов\n"
        yield "  • Временные проблемы с поисковой системой\n\n"
        yield "Продолжаю анализ на основе доступной информации...\n\n"
    
    # Шаг 3: Получаем текст со страниц (параллельно или последовательно)
    step_start = time.time()
    yield "📄 Получаю содержимое страниц...\n\n"
    logger.info(f"📝 Этап 3/4: Парсинг {len(unique_urls)} страниц (параллельно: {PARALLEL_PARSING})")
    
    texts = []
    
    if PARALLEL_PARSING:
        # Параллельная обработка для ускорения
        yield f"  ⚡ Параллельная обработка {len(unique_urls)} страниц...\n"
        tasks = [get_text_from_url(url, max_length=MAX_TEXT_LENGTH) for url in unique_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, (url, result) in enumerate(zip(unique_urls, results), 1):
            if isinstance(result, Exception):
                logger.warning(f"⚠️ Ошибка при обработке {url}: {result}")
                yield f"  ⚠️ Ошибка при обработке {i}/{len(unique_urls)}: {url[:50]}...\n"
            elif result:
                # Ограничиваем текст для AI
                text_for_ai = result[:MAX_TEXT_FOR_AI] if len(result) > MAX_TEXT_FOR_AI else result
                texts.append({"url": url, "text": text_for_ai})
                yield f"  ✅ Обработано {i}/{len(unique_urls)}: {len(text_for_ai)} символов\n"
            else:
                yield f"  ⚠️ Пустой результат {i}/{len(unique_urls)}: {url[:50]}...\n"
    else:
        # Последовательная обработка
        for i, url in enumerate(unique_urls, 1):
            yield f"  Обработка {i}/{len(unique_urls)}: {url[:50]}...\n"
            url_start = time.time()
            text = await get_text_from_url(url, max_length=MAX_TEXT_LENGTH)
            url_elapsed = time.time() - url_start
            if text:
                # Ограничиваем текст для AI
                text_for_ai = text[:MAX_TEXT_FOR_AI] if len(text) > MAX_TEXT_FOR_AI else text
                texts.append({"url": url, "text": text_for_ai})
                yield f"  ✅ Получено {len(text_for_ai)} символов ({url_elapsed:.1f}с)\n"
            else:
                yield f"  ⚠️ Не удалось получить текст ({url_elapsed:.1f}с)\n"
    
    step_elapsed = time.time() - step_start
    yield f"\n📚 Обработано {len(texts)} страниц из {len(unique_urls)} (парсинг занял {step_elapsed:.1f}с)\n\n"
    logger.info(f"✅ Этап 3 завершен за {step_elapsed:.2f}с, обработано {len(texts)} страниц")
    
    # Шаг 4: Анализируем через AI со streaming
    step_start = time.time()
    yield "🤖 Анализирую информацию через AI...\n\n"
    
    # Ограничиваем количество текста для ускорения
    texts_for_ai = texts[:MAX_URLS_TO_ANALYZE]
    total_chars = sum(len(t['text']) for t in texts_for_ai)
    logger.info(f"📝 Этап 4/4: AI-анализ ({len(texts_for_ai)} страниц, ~{total_chars} символов)")
    
    # Если нет данных, используем только запрос пользователя
    if not texts_for_ai:
        yield "⚠️ Нет данных для анализа (не удалось получить информацию с веб-страниц).\n"
        yield "Провожу анализ на основе общего знания о рынке...\n\n"
        analysis_prompt = f"""Проанализируй конкурентов в сфере: {user_request}

На основе общего знания о рынке ответь:
1. Ключевые конкуренты в этой сфере
2. Их типичные особенности
3. Общие выводы о рынке

Ответ должен быть полезным, даже без конкретных данных."""
    else:
        # Оптимизированный промпт - короче и эффективнее для ускорения
        analysis_prompt = f"""Проанализируй конкурентов: {user_request}

ИНФОРМАЦИЯ:
{chr(10).join([f"• {item['url']}: {item['text']}" for item in texts_for_ai])}

Ответь кратко:
1. Ключевые конкуренты
2. Их особенности  
3. Выводы"""
    
    # Отправляем streaming запрос в AI
    try:
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{ollama_url}/api/chat",
                json={
                    "model": "bambucha/saiga-llama3",
                    "messages": [{"role": "user", "content": analysis_prompt}],
                    "stream": True
                },
                timeout=120.0
            ) as response:
                response.raise_for_status()
                logger.info("✅ AI начал генерировать ответ (streaming)")
                chunk_count = 0
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            import json
                            chunk = json.loads(line)
                            if "message" in chunk and "content" in chunk["message"]:
                                content = chunk["message"]["content"]
                                if content:
                                    yield content
                                    chunk_count += 1
                        except Exception as e:
                            logger.debug(f"Ошибка при парсинге chunk: {e}")
                            continue
                
                step_elapsed = time.time() - step_start
                logger.info(f"✅ Этап 4 завершен за {step_elapsed:.2f}с, получено {chunk_count} chunks")
    except Exception as e:
        step_elapsed = time.time() - step_start
        logger.error(f"❌ Ошибка при AI-анализе за {step_elapsed:.2f}с: {e}")
        yield f"\n\n❌ Ошибка при анализе через AI: {str(e)}\n"
        raise
    
    total_elapsed = time.time() - total_start_time
    logger.info(f"🎉 Анализ конкурентов завершен за {total_elapsed:.2f}с ({total_elapsed/60:.1f} минут)")
    yield f"\n\n⏱️ Общее время анализа: {total_elapsed:.1f}с ({total_elapsed/60:.1f} минут)\n"

