import asyncio
from app.services.llm.factory import LLMFactory
from app.services.llm.base import LLMMessage

async def main():
    provider = LLMFactory.get_provider()

    messages = [
        LLMMessage(
            role="user",
            content="Hello! Introduce yourself in two sentences."
        )
    ]

    print("Testing Ollama...\n")

    response = await provider.generate_chat(
        messages,
        model="qwen2.5:3b"
    )

    print("Ollama Response:")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())