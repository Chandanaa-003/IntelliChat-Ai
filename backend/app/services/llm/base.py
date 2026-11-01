from abc import ABC, abstractmethod
from typing import AsyncGenerator, List, Dict, Any, Optional
from pydantic import BaseModel


class LLMMessage(BaseModel):
    role: str  # "user", "assistant", "system"
    content: str


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM inference providers."""

    @abstractmethod
    async def stream_chat(
        self,
        messages: List[LLMMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = 2048,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        """Stream response tokens asynchronously."""
        yield ""

    @abstractmethod
    async def generate_chat(
        self,
        messages: List[LLMMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = 2048,
        **kwargs: Any,
    ) -> str:
        """Generate complete response in one call."""
        pass
