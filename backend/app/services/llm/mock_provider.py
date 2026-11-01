import asyncio
from typing import AsyncGenerator, List, Any, Optional
import re

from app.services.llm.base import BaseLLMProvider, LLMMessage


class MockLLMProvider(BaseLLMProvider):
    """
    Intelligent built-in assistant provider.
    Generates rich, contextual responses with Markdown and code blocks,
    streaming token-by-token with realistic latency.
    """

    async def stream_chat(
        self,
        messages: List[LLMMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = 2048,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        full_response = self._synthesize_response(messages)

        # Stream word by word / chunk by chunk to mimic real token streaming
        words = re.findall(r"\S+|\s+", full_response)
        for i, word in enumerate(words):
            yield word
            # Sleep slightly every 1-2 words
            if i % 2 == 0:
                await asyncio.sleep(0.02)

    async def generate_chat(
        self,
        messages: List[LLMMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = 2048,
        **kwargs: Any,
    ) -> str:
        return self._synthesize_response(messages)

    def _synthesize_response(self, messages: List[LLMMessage]) -> str:
        if not messages:
            return "Hello! How can I assist you today?"

        last_user_msg = next((m.content for m in reversed(messages) if m.role == "user"), "").strip().lower()
        history_length = len(messages)

        # Contextual intelligence based on query keywords
        if any(w in last_user_msg for w in ["hi", "hello", "hey", "greetings"]):
            return (
                "👋 **Hello! Welcome to IntelliChat.**\n\n"
                "I am your production-ready AI Assistant. Here are a few things I can help you with:\n\n"
                "- 🚀 **Full-Stack Engineering**: Python, FastAPI, React, TypeScript, and SQL\n"
                "- 🧠 **AI & LLM Integration**: Multi-provider routing, streaming, and embeddings\n"
                "- 📊 **Data & Architecture**: System design, database optimization, and cloud deployment\n\n"
                "How can I help you today?"
            )

        elif any(w in last_user_msg for w in ["code", "python", "fastapi", "react", "typescript", "function", "example"]):
            return (
                "Here is a clean, production-ready implementation that demonstrates modern design patterns:\n\n"
                "```python\n"
                "# Example: Asynchronous Task Processor with FastAPI\n"
                "import asyncio\n"
                "from typing import AsyncGenerator\n\n"
                "async def stream_tokens(prompt: str) -> AsyncGenerator[str, None]:\n"
                "    tokens = [\"Exploring\", \" the\", \" power\", \" of\", \" streaming\", \" AI!\"]\n"
                "    for token in tokens:\n"
                "        await asyncio.sleep(0.05)\n"
                "        yield token\n"
                "```\n\n"
                "### Key Advantages:\n"
                "1. **Non-blocking I/O**: Keeps the event loop responsive under high concurrency.\n"
                "2. **Memory Efficiency**: Streams chunks without buffering the full response in memory.\n"
                "3. **Real-time UX**: Eliminates wait time for users by streaming tokens as they arrive.\n\n"
                "Would you like me to adapt this for your specific use case?"
            )

        elif any(w in last_user_msg for w in ["database", "postgres", "sql", "sqlite"]):
            return (
                "### 🗄️ Database Architecture & Persistence\n\n"
                "Our application leverages **SQLAlchemy 2.0 Async** with full support for:\n\n"
                "1. **PostgreSQL** (via `asyncpg` for high-throughput production workloads)\n"
                "2. **SQLite** (via `aiosqlite` for zero-configuration local development & testing)\n\n"
                "```sql\n"
                "-- High-performance indexing for chat messages\n"
                "CREATE INDEX idx_messages_conv_created \n"
                "ON messages (conversation_id, created_at DESC);\n"
                "```\n\n"
                "Is there a specific query or migration you'd like to optimize?"
            )

        elif any(w in last_user_msg for w in ["who are you", "what are you", "model", "capabilities"]):
            return (
                "### 🤖 About IntelliChat AI\n\n"
                "I am an intelligent, production-ready AI conversational assistant built with:\n\n"
                "- **Backend Engine**: FastAPI with asynchronous session management\n"
                "- **Real-time Transport**: Server-Sent Events (SSE) token streaming\n"
                "- **Storage**: Relational database with full chat persistence and JWT authentication\n"
                "- **LLM Integrations**: Pluggable support for Groq, OpenAI, Google Gemini, Hugging Face, and local offline inference.\n\n"
                "Feel free to ask me questions, request code reviews, or design system architectures!"
            )

        elif history_length > 2 and any(w in last_user_msg for w in ["explain", "why", "how", "more"]):
            return (
                f"Continuing from our discussion:\n\n"
                f"When addressing **\"{last_user_msg}\"**, the most effective approach breaks down into three core stages:\n\n"
                f"1. **Analysis & Scope**: Identifying constraints and target latency.\n"
                f"2. **Execution**: Implementing clean, decoupled modules with comprehensive unit tests.\n"
                f"3. **Verification**: Validating token efficiency and UI responsiveness.\n\n"
                f"Would you like to dive deeper into any specific aspect?"
            )

        else:
            return (
                f"Thank you for your question about **\"{last_user_msg}\"**!\n\n"
                f"Here is a comprehensive breakdown:\n\n"
                f"1. **Core Concept**: Understanding the fundamental mechanics behind this requirement.\n"
                f"2. **Best Practices**: Designing maintainable, modular components with strong type safety.\n"
                f"3. **Scalability**: Ensuring zero-downtime performance and graceful failure handling.\n\n"
                f"> 💡 **Tip**: You can configure live API keys for Groq, OpenAI, Gemini, or Hugging Face in `backend/.env` at any time to switch from mock to live neural models.\n\n"
                f"Let me know if you would like me to generate code or provide further details!"
            )
