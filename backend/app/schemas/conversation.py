from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class ConversationCreate(BaseModel):
    title: Optional[str] = Field(default="New Chat", max_length=255)
    model: Optional[str] = Field(default="smart-assistant-v1", max_length=100)
    system_prompt: Optional[str] = None


class ConversationUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    model: Optional[str] = Field(None, max_length=100)
    system_prompt: Optional[str] = None


class ConversationResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    title: str
    model: str
    system_prompt: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)
