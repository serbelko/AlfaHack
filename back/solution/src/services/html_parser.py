"""
Сервис для парсинга HTML и извлечения текста
"""
import httpx
import logging
import time
from bs4 import BeautifulSoup
from typing import Optional
from ..config import MAX_HTML_LENGTH

logger = logging.getLogger(__name__)


async def fetch_html(url: str, timeout: float = 10.0) -> Optional[str]:
    """
    Получает HTML содержимое страницы
    
    Args:
        url: URL страницы
        timeout: Таймаут запроса
        
    Returns:
        HTML содержимое или None при ошибке
    """
    start_time = time.time()
    logger.debug(f"📥 Загружаю HTML с {url[:60]}...")
    
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            response.raise_for_status()
            html = response.text[:MAX_HTML_LENGTH]  # Ограничиваем длину
            
            elapsed = time.time() - start_time
            logger.debug(f"✅ HTML загружен ({len(html)} символов) за {elapsed:.2f}с")
            
            return html
    except Exception as e:
        elapsed = time.time() - start_time
        logger.warning(f"⚠️ Ошибка при загрузке HTML с {url[:60]} за {elapsed:.2f}с: {e}")
        return None


def extract_text_from_html(html: str, max_length: int = 5000) -> str:
    """
    Извлекает текст из HTML с ограничением по длине
    
    Args:
        html: HTML содержимое
        max_length: Максимальная длина извлекаемого текста
        
    Returns:
        Извлеченный текст
    """
    try:
        soup = BeautifulSoup(html, 'lxml')
        
        # Удаляем скрипты и стили
        for script in soup(["script", "style", "meta", "link"]):
            script.decompose()
        
        # Извлекаем текст
        text = soup.get_text(separator=' ', strip=True)
        
        # Очищаем от лишних пробелов
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Ограничиваем длину
        original_length = len(text)
        if len(text) > max_length:
            text = text[:max_length] + "..."
            logger.debug(f"📝 Текст обрезан с {original_length} до {max_length} символов")
        
        return text
    except Exception as e:
        logger.error(f"❌ Ошибка при парсинге HTML: {e}")
        return ""


async def get_text_from_url(url: str, max_length: int = 5000) -> str:
    """
    Получает текст с веб-страницы
    
    Args:
        url: URL страницы
        max_length: Максимальная длина текста
        
    Returns:
        Извлеченный текст
    """
    start_time = time.time()
    logger.info(f"📄 Обрабатываю страницу: {url[:60]}...")
    
    html = await fetch_html(url)
    if html:
        text = extract_text_from_html(html, max_length)
        elapsed = time.time() - start_time
        logger.info(f"✅ Текст извлечен ({len(text)} символов) за {elapsed:.2f}с")
        return text
    
    elapsed = time.time() - start_time
    logger.warning(f"⚠️ Не удалось получить текст за {elapsed:.2f}с")
    return ""

