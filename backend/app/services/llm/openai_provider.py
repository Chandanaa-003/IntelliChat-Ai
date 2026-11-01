import json
import logging
from typing import AsyncGenerator, List, Any, Optional
import httpx

from app.services.llm.base import BaseLLMProvider, LLMMessage

logger = logging.getLogger(__name__)


class OpenAICompatibleProvider(BaseLLMProvider):
    """
    Provider supporting OpenAI, Groq, OpenRouter, DeepSeek, and any OpenAI-compatible endpoint.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        default_model: str = "gpt-3.5-turbo",
    ):
        self.api_key = api_key
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
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model or self.default_model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                async with client.stream("POST", url, headers=headers, json=payload) as response:
                    if response.status_code != 200:
                        error_body = await response.aread()
                        error_message = error_body.decode(errors="replace")
                        logger.error(
                            "OpenAI-compatible API error %s: %s",
                            response.status_code,
                            error_message,
                        )
                        raise RuntimeError(
                            f"AI provider returned HTTP {response.status_code}: "
                            f"{error_message}"
                        )

                    async for line in response.aiter_lines():
                        line = line.strip()
                        if not line or not line.startswith("data:"):
                            continue
                        data_str = line[5:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            delta = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if delta:
                                yield delta
                        except json.JSONDecodeError:
                            continue
            except httpx.RequestError as exc:
                logger.exception("Network error communicating with AI provider")
                raise RuntimeError(
                    f"Could not connect to AI provider: {exc}"
                ) from exc

    async def generate_chat(
        self,
        messages: List[LLMMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = 2048,
        **kwargs: Any,
    ) -> str:
        tokens = []
        async for token in self.stream_chat(messages, model, temperature, max_tokens, **kwargs):
            tokens.append(token)
        return "".join(tokens)
