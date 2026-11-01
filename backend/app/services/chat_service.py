
import json
import logging
from typing import AsyncGenerator, Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy import delete

from app.core.config import settings
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.chat import ChatStreamRequest, RegenerateRequest
from app.schemas.conversation import ConversationCreate
from app.services.conversation_service import ConversationService
from app.services.llm.factory import LLMFactory
from app.services.llm.base import LLMMessage

logger = logging.getLogger(__name__)

DEFAULT_SYSTEM_PROMPT = (
    "You are IntelliChat, an advanced, helpful, and highly intelligent AI assistant. "
    "Provide clear, accurate, and insightful answers with properly formatted Markdown, "
    "including code blocks with language specifiers where applicable."
)


class ChatService:

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        return max(1, len(text) // 4)

    @staticmethod
    async def build_context_messages(
        db: AsyncSession,
        conversation: Conversation,
        new_user_message: Optional[str] = None,
        max_history_turns: int = 20,
        exclude_last_assistant: bool = False,
    ) -> List[LLMMessage]:

        messages: List[LLMMessage] = []

        system_content = conversation.system_prompt or DEFAULT_SYSTEM_PROMPT

        messages.append(
            LLMMessage(role="system", content=system_content)
        )

        history = await ConversationService.get_messages(
            db,
            conversation_id=conversation.id,
            limit=max_history_turns,
        )

        if exclude_last_assistant and history and history[-1].role == "assistant":
            history = history[:-1]

        for msg in history:
            messages.append(
                LLMMessage(role=msg.role, content=msg.content)
            )

        if new_user_message:
            messages.append(
                LLMMessage(role="user", content=new_user_message)
            )

        return messages

    @staticmethod
    async def stream_chat_response(
        db: AsyncSession,
        request: ChatStreamRequest,
        user_id: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:

        # Step 1: Resolve conversation
        if request.conversation_id:
            conv = await ConversationService.get_conversation(
                db, request.conversation_id, user_id
            )
        else:
            words = request.content.split()
            title_preview = " ".join(words[:6])

            if len(words) > 6:
                title_preview += "..."

            conv = await ConversationService.create_conversation(
                db=db,
                user_id=user_id,
                data=ConversationCreate(
                    title=title_preview or "New Chat",
                    model=request.model or settings.DEFAULT_MODEL,
                    system_prompt=request.system_prompt,
                ),
            )

        # Step 2: Store user message
        user_tokens = ChatService._estimate_tokens(request.content)

        user_msg = await ConversationService.add_message(
            db=db,
            conversation_id=conv.id,
            role="user",
            content=request.content,
            token_count=user_tokens,
        )

        session_data = {
            "conversation_id": conv.id,
            "title": conv.title,
            "user_message_id": user_msg.id,
        }

        yield f"event: session\ndata: {json.dumps(session_data)}\n\n"

        # Step 3: Build context
        llm_messages = await ChatService.build_context_messages(db, conv)

        # Step 4: Select configured LLM provider
        model_name = (
            request.model
            or conv.model
            or settings.DEFAULT_MODEL
        )

        provider_name = LLMFactory.get_provider_name_for_model(model_name)

        logger.info(
            "Using LLM provider: %s | Model: %s",
            provider_name,
            model_name,
        )

        accumulated_chunks: List[str] = []

        try:
            provider = LLMFactory.get_provider(provider_name)
            async for token_chunk in provider.stream_chat(
                llm_messages,
                model=model_name,
            ):
                if token_chunk:
                    accumulated_chunks.append(token_chunk)

                    token_data = {"delta": token_chunk}

                    yield (
                        f"event: token\ndata: "
                        f"{json.dumps(token_data)}\n\n"
                    )

            if not accumulated_chunks:
                raise RuntimeError("The configured AI model returned an empty response.")

        except Exception as e:
            logger.exception("Streaming error occurred")

            error_data = {"error": str(e)}

            yield (
                f"event: error\ndata: "
                f"{json.dumps(error_data)}\n\n"
            )
            return

        # Step 5: Save assistant response
        full_reply = "".join(accumulated_chunks)

        assistant_tokens = ChatService._estimate_tokens(full_reply)

        assistant_msg = await ConversationService.add_message(
            db=db,
            conversation_id=conv.id,
            role="assistant",
            content=full_reply,
            token_count=assistant_tokens,
        )

        done_data = {
            "conversation_id": conv.id,
            "message_id": assistant_msg.id,
            "token_count": assistant_tokens,
            "created_at": str(assistant_msg.created_at),
        }

        yield f"event: done\ndata: {json.dumps(done_data)}\n\n"

    @staticmethod
    async def regenerate_response(
        db: AsyncSession,
        request: RegenerateRequest,
        user_id: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:

        conv = await ConversationService.get_conversation(
            db, request.conversation_id, user_id
        )

        messages = await ConversationService.get_messages(
            db, conv.id
        )

        if not messages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No messages found in conversation to regenerate.",
            )

        # Keep the previous answer until the replacement has been generated.
        message_to_replace = None
        if messages[-1].role == "assistant":
            message_to_replace = messages[-1]

        # Build context
        llm_messages = await ChatService.build_context_messages(
            db, conv, exclude_last_assistant=True
        )

        model_name = (
            request.model
            or conv.model
            or settings.DEFAULT_MODEL
        )

        provider_name = LLMFactory.get_provider_name_for_model(model_name)

        logger.info(
            "Regenerating with provider: %s | Model: %s",
            provider_name,
            model_name,
        )

        accumulated_chunks: List[str] = []

        session_data = {
            "conversation_id": conv.id,
            "regenerated": True,
        }

        yield f"event: session\ndata: {json.dumps(session_data)}\n\n"

        try:
            provider = LLMFactory.get_provider(provider_name)
            async for token_chunk in provider.stream_chat(
                llm_messages,
                model=model_name,
            ):
                if token_chunk:
                    accumulated_chunks.append(token_chunk)

                    token_data = {"delta": token_chunk}

                    yield (
                        f"event: token\ndata: "
                        f"{json.dumps(token_data)}\n\n"
                    )

            if not accumulated_chunks:
                raise RuntimeError("The configured AI model returned an empty response.")

        except Exception as e:
            logger.exception("Regeneration error")

            error_data = {"error": str(e)}

            yield (
                f"event: error\ndata: "
                f"{json.dumps(error_data)}\n\n"
            )
            return

        full_reply = "".join(accumulated_chunks)

        if message_to_replace:
            stmt = delete(Message).where(Message.id == message_to_replace.id)
            await db.execute(stmt)
            await db.commit()

        assistant_tokens = ChatService._estimate_tokens(full_reply)

        assistant_msg = await ConversationService.add_message(
            db=db,
            conversation_id=conv.id,
            role="assistant",
            content=full_reply,
            token_count=assistant_tokens,
        )

        done_data = {
            "conversation_id": conv.id,
            "message_id": assistant_msg.id,
            "token_count": assistant_tokens,
            "created_at": str(assistant_msg.created_at),
        }

        yield f"event: done\ndata: {json.dumps(done_data)}\n\n"
