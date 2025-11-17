import json
import asyncio
import httpx
from fastapi.responses import StreamingResponse
from .config import OLLAMA_URL
from .schemas import PromptRequest

from ollama import Client
ollama_client = Client(
  host=OLLAMA_URL,
)

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


async def get_ai_message(payload: PromptRequest) -> str:
    """
    Обработчик для получения ответа от AI.
    
    Args:
        payload: Запрос с промптом пользователя
        
    Returns:
        Ответ от AI модели
    """
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

    async with httpx.AsyncClient() as client:
        response = await client.post(
            OLLAMA_URL,
            json={"prompt": classification_prompt, "stream": False},
            timeout=30.0
        )
        response.raise_for_status()

        response_data = response.json()
        if response_data["message"] == "[FIN]":
            return "FIN"
        elif response_data["message"] == "[MRKT]":
            return "MRKT"

