
import json
import logging
from typing import AsyncGenerator, List, Any, Optional

import httpx

from app.services.llm.base import BaseLLMProvider, LLMMessage

logger = logging.getLogger(__name__)


class OllamaProvider(BaseLLMProvider):

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        default_model: str = "qwen2.5:3b",
    ):
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model

    async def stream_chat(
        self,
        messages: List[LLMMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = 2048,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:

        model_name = model or self.default_model

        # Remove provider prefix if present
        if model_name.startswith("ollama:"):
            model_name = model_name.replace("ollama:", "", 1)

        payload = {
            "model": model_name,
            "messages": [
                {"role": m.role, "content": m.content}
                for m in messages
            ],
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens or 2048,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/chat",
                    json=payload,
                ) as response:

                    if response.status_code != 200:
                        error = await response.aread()
                        raise RuntimeError(
                            f"Ollama error {response.status_code}: "
                            f"{error.decode(errors='replace')}"
                        )

                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue

                        data = json.loads(line)

                        content = (
                            data.get("message", {}).get("content", "")
                        )

                        if content:
                            yield content

                        if data.get("done"):
                            break

        except Exception:
            logger.exception("Ollama streaming failed")
            raise

    async def generate_chat(
        self,
        messages: List[LLMMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = 2048,
        **kwargs: Any,
    ) -> str:

        result = []

        async for chunk in self.stream_chat(
            messages,
            model,
            temperature,
            max_tokens,
            **kwargs,
        ):
            result.append(chunk)

        return "".join(result)
