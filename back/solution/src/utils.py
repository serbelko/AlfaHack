import json


def parse_model_response(response: str) -> dict | None:
        """
        Парсит ответ модели, пытаясь найти команду для вызова API.
        Это самая сложная и важная часть. Нужно договориться с моделью о формате.
        Поддерживает два формата:
        1. Новый формат: {"endpoints": ["/api/amount/", "/api/amount/history"]}
        2. Старый формат (для обратной совместимости): {"endpoint": "/api/amount/"}
        """
        # Простейший парсинг: ищем JSON в ответе
        try:
            # Пытаемся найти JSON-объект в тексте
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = response[start:end]
                action_data = json.loads(json_str)
                return action_data

        except json.JSONDecodeError:
            pass
        return None