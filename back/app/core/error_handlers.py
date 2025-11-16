"""
Модуль для форматирования и обработки ошибок.
"""
from typing import Any, Dict, List, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logger import get_logger

logger = get_logger(__name__)


def format_validation_error(errors: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Форматирует ошибки валидации в читаемый вид.
    
    Args:
        errors: Список ошибок валидации от Pydantic
        
    Returns:
        Отформатированный словарь с ошибками
    """
    formatted_errors = []
    
    for error in errors:
        # Извлекаем информацию об ошибке
        error_type = error.get("type", "unknown")
        error_loc = error.get("loc", [])
        error_msg = error.get("msg", "Validation error")
        error_input = error.get("input")
        
        # Определяем тип локации (body, query, path, header)
        location = "body"
        field_path = []
        
        if error_loc:
            # Первый элемент обычно указывает на тип (body, query, path, header)
            if len(error_loc) > 0 and error_loc[0] in ["query", "path", "header", "body"]:
                location = error_loc[0]
                field_path = list(error_loc[1:]) if len(error_loc) > 1 else []
            else:
                # Если первый элемент не тип, то это путь к полю
                field_path = list(error_loc)
        
        # Формируем путь к полю
        field = ".".join(str(part) for part in field_path) if field_path else "unknown"
        
        # Улучшаем сообщение об ошибке
        message = _improve_error_message(error_type, error_msg, field)
        
        formatted_errors.append({
            "field": field,
            "message": message,
            "location": location,
            "type": error_type,
            "input": error_input if error_input is not None else None,
        })
    
    return {
        "error": "Validation Error",
        "message": "Ошибка валидации данных запроса",
        "status_code": 422,
        "details": formatted_errors,
    }


def _improve_error_message(error_type: str, original_msg: str, field: str) -> str:
    """
    Улучшает сообщение об ошибке, делая его более понятным.
    
    Args:
        error_type: Тип ошибки от Pydantic
        original_msg: Оригинальное сообщение
        field: Имя поля
        
    Returns:
        Улучшенное сообщение
    """
    # Русские сообщения для распространённых ошибок
    error_messages = {
        "missing": f"Поле '{field}' обязательно для заполнения",
        "value_error.missing": f"Поле '{field}' обязательно для заполнения",
        "type_error.missing": f"Поле '{field}' обязательно для заполнения",
        "value_error": f"Некорректное значение поля '{field}'",
        "type_error": f"Некорректный тип данных для поля '{field}'",
        "value_error.str.regex": f"Поле '{field}' не соответствует требуемому формату",
        "value_error.email": f"Поле '{field}' должно быть валидным email адресом",
        "value_error.url": f"Поле '{field}' должно быть валидным URL",
        "value_error.number.not_gt": f"Поле '{field}' должно быть больше указанного значения",
        "value_error.number.not_ge": f"Поле '{field}' должно быть больше или равно указанному значению",
        "value_error.number.not_lt": f"Поле '{field}' должно быть меньше указанного значения",
        "value_error.number.not_le": f"Поле '{field}' должно быть меньше или равно указанному значению",
        "value_error.list.min_items": f"Список '{field}' должен содержать минимум элементов",
        "value_error.list.max_items": f"Список '{field}' должен содержать максимум элементов",
        "value_error.str.min_length": f"Поле '{field}' слишком короткое",
        "value_error.str.max_length": f"Поле '{field}' слишком длинное",
        "value_error.any_str.min_length": f"Поле '{field}' слишком короткое",
        "value_error.any_str.max_length": f"Поле '{field}' слишком длинное",
    }
    
    # Пытаемся найти улучшенное сообщение
    for error_key, message in error_messages.items():
        if error_key in error_type.lower():
            return message
    
    # Если не нашли, возвращаем оригинальное сообщение с контекстом
    if field and field != "unknown":
        return f"Ошибка в поле '{field}': {original_msg}"
    return original_msg


def format_http_error(exc: StarletteHTTPException, request: Request) -> Dict[str, Any]:
    """
    Форматирует HTTP ошибку в читаемый вид.
    
    Args:
        exc: HTTP исключение
        request: Объект запроса
        
    Returns:
        Отформатированный словарь с ошибкой
    """
    status_code = exc.status_code
    detail = exc.detail
    path = request.url.path.lower()
    
    # Улучшаем сообщения для распространённых кодов ошибок
    error_messages = {
        400: "Некорректный запрос",
        401: "Требуется аутентификация",
        403: "Доступ запрещён",
        404: "Ресурс не найден",
        405: "Метод не разрешён",
        409: "Конфликт данных",
        422: "Ошибка валидации",
        429: "Слишком много запросов",
        500: "Внутренняя ошибка сервера",
        502: "Ошибка шлюза",
        503: "Сервис недоступен",
    }
    
    error_title = error_messages.get(status_code, "Ошибка")
    
    # Специальная обработка для 404 ошибок в зависимости от контекста
    if status_code == 404:
        # Проверяем, связана ли ошибка с пользователем
        detail_str = str(detail).lower()
        # Определяем, что это ошибка пользователя по пути или по сообщению
        is_user_error = (
            "/api/auth" in path or
            ("user" in detail_str and ("not found" in detail_str or "не найден" in detail_str)) or
            "пользователь не найден" in detail_str
        )
        
        if is_user_error:
            error_title = "Пользователь не найден"
    
    # Если detail уже словарь, объединяем его с базовой структурой
    if isinstance(detail, dict):
        result = {
            "error": error_title,
            "status_code": status_code,
        }
        # Добавляем поля из detail, но не перезаписываем error и status_code
        for key, value in detail.items():
            if key not in ["error", "status_code"]:
                result[key] = value
        return result
    
    # Если detail строка, оборачиваем её
    # Для 404 ошибок пользователя улучшаем сообщение
    message = str(detail)
    if status_code == 404 and error_title == "Пользователь не найден":
        if message.upper() == "NOT FOUND" or message == "NOT FOUND":
            message = "Пользователь не найден"
    
    return {
        "error": error_title,
        "message": message,
        "status_code": status_code,
    }


def format_general_error(exc: Exception, request: Request) -> Dict[str, Any]:
    """
    Форматирует общую ошибку (500).
    
    Args:
        exc: Исключение
        request: Объект запроса
        
    Returns:
        Отформатированный словарь с ошибкой
    """
    return {
        "error": "Internal Server Error",
        "message": "Произошла внутренняя ошибка сервера",
        "status_code": 500,
        "type": type(exc).__name__,
    }


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Обработчик HTTP исключений.
    
    Args:
        request: Объект запроса
        exc: HTTP исключение
        
    Returns:
        JSON ответ с ошибкой
    """
    logger.warning(
        f"HTTP exception: {exc.status_code} - {exc.detail} - "
        f"Path: {request.url.path} - Method: {request.method}"
    )
    
    formatted_error = format_http_error(exc, request)
    
    return JSONResponse(
        status_code=exc.status_code,
        content=formatted_error,
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Обработчик ошибок валидации (422).
    
    Args:
        request: Объект запроса
        exc: Ошибка валидации
        
    Returns:
        JSON ответ с ошибкой валидации
    """
    logger.warning(
        f"Validation error: {exc.errors()} - "
        f"Path: {request.url.path} - Method: {request.method}"
    )
    
    formatted_error = format_validation_error(exc.errors())
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=formatted_error,
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Обработчик всех остальных исключений (500).
    
    Args:
        request: Объект запроса
        exc: Исключение
        
    Returns:
        JSON ответ с ошибкой
    """
    logger.error(
        f"Unhandled exception: {type(exc).__name__} - {str(exc)} - "
        f"Path: {request.url.path} - Method: {request.method}",
        exc_info=True,
    )
    
    formatted_error = format_general_error(exc, request)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=formatted_error,
    )

