from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


class MessageCreate(BaseModel):
    conversation_id: Optional[str] = None
    content: str = Field(..., min_length=1)
    role: Literal["user", "assistant", "system"] = "user"
    model: Optional[str] = None


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    token_count: int = 0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatStreamRequest(BaseModel):
    conversation_id: Optional[str] = None
    content: str = Field(..., min_length=1)
    model: Optional[str] = None
    system_prompt: Optional[str] = None


class RegenerateRequest(BaseModel):
    conversation_id: str
    message_id: Optional[str] = None
    model: Optional[str] = None


class StreamChunk(BaseModel):
    event: Literal["token", "meta", "done", "error"] = "token"
    data: dict
