from pydantic import BaseModel


class PromptRequest(BaseModel):
    prompt: str


class AIResponse(BaseModel):
    message: str

