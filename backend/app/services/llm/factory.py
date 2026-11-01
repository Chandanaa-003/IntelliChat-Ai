
from typing import Optional

from app.core.config import settings
from app.services.llm.base import BaseLLMProvider
from app.services.llm.mock_provider import MockLLMProvider
from app.services.llm.openai_provider import OpenAICompatibleProvider
from app.services.llm.huggingface_provider import HuggingFaceProvider
from app.services.llm.ollama_provider import OllamaProvider


class LLMFactory:

    MOCK_MODEL_ID = "smart-assistant-v1"

    @staticmethod
    def list_available_models() -> list[dict[str, object]]:
        """Return the configured model and the built-in offline fallback."""
        configured_provider = settings.DEFAULT_LLM_PROVIDER.strip().lower()
        models: list[dict[str, object]] = []

        if configured_provider != "mock":
            models.append(
                {
                    "id": settings.DEFAULT_MODEL,
                    "name": settings.DEFAULT_MODEL,
                    "provider": configured_provider,
                    "is_active": True,
                    "description": f"Configured {configured_provider} model",
                }
            )

        models.append(
            {
                "id": LLMFactory.MOCK_MODEL_ID,
                "name": "Smart Assistant",
                "provider": "mock",
                "is_active": configured_provider == "mock",
                "description": "Built-in intelligent offline assistant",
            }
        )
        return models

    @staticmethod
    def get_provider_name_for_model(model: Optional[str] = None) -> str:
        if model:
            for available_model in LLMFactory.list_available_models():
                if available_model["id"] == model:
                    return str(available_model["provider"])
        return settings.DEFAULT_LLM_PROVIDER.strip().lower()

    @staticmethod
    def get_provider(
        provider_name: Optional[str] = None
    ) -> BaseLLMProvider:

        name = (
            provider_name or settings.DEFAULT_LLM_PROVIDER
        ).strip().lower()

        model = settings.DEFAULT_MODEL

        # OLLAMA - Local AI
        if name == "ollama":
            return OllamaProvider(
                base_url=settings.OLLAMA_BASE_URL,
                default_model=model,
            )

        # GROQ
        if name == "groq":
            if not settings.GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY is missing.")

            return OpenAICompatibleProvider(
                api_key=settings.GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1",
                default_model=model,
            )

        # OPENAI
        if name == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is missing.")

            return OpenAICompatibleProvider(
                api_key=settings.OPENAI_API_KEY,
                base_url="https://api.openai.com/v1",
                default_model=model,
            )

        # HUGGING FACE
        if name == "huggingface":
            if not settings.HUGGINGFACE_API_KEY:
                raise ValueError("HUGGINGFACE_API_KEY is missing.")

            return HuggingFaceProvider(
                api_key=settings.HUGGINGFACE_API_KEY,
                default_model=model,
            )

        # MOCK
        if name == "mock":
            return MockLLMProvider()

        raise ValueError(
            f"Unsupported LLM provider: {name}. "
            "Available providers: ollama, groq, openai, "
            "huggingface, mock."
        )

    @staticmethod
    def get_llm_provider(
        provider_name: Optional[str] = None
    ) -> BaseLLMProvider:
        return LLMFactory.get_provider(provider_name)
