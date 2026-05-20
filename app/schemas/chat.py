from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    id: str
    role: str
    content: str


class ConversationHistory(BaseModel):
    agent_id: str
    messages: list[ChatResponse]