import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/")
API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000")
SERVICE_API_TOKEN = os.getenv("SERVICE_API_TOKEN")

# Лимиты для работы с AI и текстом
MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", "3000"))  # Максимальная длина текста для анализа (уменьшено для скорости)
MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "3"))  # Количество ссылок на запрос (уменьшено для скорости)
MAX_HTML_LENGTH = int(os.getenv("MAX_HTML_LENGTH", "8000"))  # Максимальная длина HTML для парсинга
MAX_URLS_TO_ANALYZE = int(os.getenv("MAX_URLS_TO_ANALYZE", "5"))  # Максимум страниц для анализа (для ускорения)
MAX_TEXT_FOR_AI = int(os.getenv("MAX_TEXT_FOR_AI", "500"))  # Максимальная длина текста для передачи в AI (на страницу)
PARALLEL_PARSING = os.getenv("PARALLEL_PARSING", "true").lower() == "true"  # Параллельная обработка страниц

