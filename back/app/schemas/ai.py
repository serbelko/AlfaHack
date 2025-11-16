from pydantic import BaseModel

from app.services.ai import AISegment


class PromptRequest(BaseModel):
    prompt: str


class AIResponse(BaseModel):
    segment: AISegment
