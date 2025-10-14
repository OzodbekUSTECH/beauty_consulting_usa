from datetime import datetime
from typing import Optional, List, Tuple

from pydantic import BaseModel, Field


class CreatePromptRequest(BaseModel):
    tg_id: str
    username: Optional[str] = None
    name: Optional[str] = None
    phone_number: Optional[str] = None
    prompt: str

    created_at: datetime = Field(default_factory=datetime.now)


class AssistantResponse(BaseModel):
    response: Optional[str] = None

class SetAssistantStateRequest(BaseModel):
    enabled: bool

class AssistantStateResponse(SetAssistantStateRequest):
    pass