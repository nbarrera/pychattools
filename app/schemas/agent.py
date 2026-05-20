from pydantic import BaseModel
from datetime import datetime


class AgentCreate(BaseModel):
    name: str
    persona: str


class AgentResponse(BaseModel):
    id: str
    name: str
    persona: str
    created_at: datetime

    model_config = {"from_attributes": True}