from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, desc
from fastapi import HTTPException, status

from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.conversation import ConversationCreate, ConversationUpdate, ConversationResponse
from app.schemas.chat import MessageResponse


class ConversationService:
    @staticmethod
    async def create_conversation(
        db: AsyncSession,
        user_id: Optional[str],
        data: ConversationCreate,
    ) -> Conversation:
        """Create a new chat conversation session."""
        conv = Conversation(
            user_id=user_id,
            title=data.title or "New Chat",
            model=data.model or "smart-assistant-v1",
            system_prompt=data.system_prompt,
        )
        db.add(conv)
        await db.commit()
        await db.refresh(conv)
        return conv

    @staticmethod
    async def list_conversations(
        db: AsyncSession,
        user_id: Optional[str],
        limit: int = 50,
        offset: int = 0,
        search: Optional[str] = None,
    ) -> List[ConversationResponse]:
        """List conversations for a given user (or anonymous sessions) with message counts."""
        # Query conversations ordered by updated_at desc
        stmt = select(Conversation).order_by(desc(Conversation.updated_at))

        if user_id:
            stmt = stmt.where(Conversation.user_id == user_id)
        else:
            # For anonymous/guest mode without auth, retrieve unassigned sessions
            stmt = stmt.where(Conversation.user_id.is_(None))

        if search:
            stmt = stmt.where(Conversation.title.ilike(f"%{search}%"))

        stmt = stmt.limit(limit).offset(offset)
        result = await db.execute(stmt)
        conversations = result.scalars().all()

        responses = []
        for conv in conversations:
            # Count messages
            count_stmt = select(func.count(Message.id)).where(Message.conversation_id == conv.id)
            count_result = await db.execute(count_stmt)
            msg_count = count_result.scalar() or 0

            item = ConversationResponse(
                id=conv.id,
                user_id=conv.user_id,
                title=conv.title,
                model=conv.model,
                system_prompt=conv.system_prompt,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=msg_count,
            )
            responses.append(item)

        return responses

    @staticmethod
    async def get_conversation(
        db: AsyncSession,
        conversation_id: str,
        user_id: Optional[str] = None,
    ) -> Conversation:
        """Fetch a specific conversation by ID with permission check."""
        stmt = select(Conversation).where(Conversation.id == conversation_id)
        result = await db.execute(stmt)
        conv = result.scalars().first()

        if not conv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found.",
            )

        if user_id and conv.user_id and conv.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this conversation.",
            )

        return conv

    @staticmethod
    async def update_conversation(
        db: AsyncSession,
        conversation_id: str,
        data: ConversationUpdate,
        user_id: Optional[str] = None,
    ) -> Conversation:
        """Update conversation title or model."""
        conv = await ConversationService.get_conversation(db, conversation_id, user_id)

        if data.title is not None:
            conv.title = data.title
        if data.model is not None:
            conv.model = data.model
        if data.system_prompt is not None:
            conv.system_prompt = data.system_prompt

        await db.commit()
        await db.refresh(conv)
        return conv

    @staticmethod
    async def delete_conversation(
        db: AsyncSession,
        conversation_id: str,
        user_id: Optional[str] = None,
    ) -> None:
        """Delete conversation and its associated messages."""
        conv = await ConversationService.get_conversation(db, conversation_id, user_id)
        await db.delete(conv)
        await db.commit()

    @staticmethod
    async def get_messages(
        db: AsyncSession,
        conversation_id: str,
        limit: int = 100,
    ) -> List[MessageResponse]:
        """Get ordered messages for a conversation."""
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        messages = result.scalars().all()
        return [MessageResponse.model_validate(msg) for msg in messages]

    @staticmethod
    async def add_message(
        db: AsyncSession,
        conversation_id: str,
        role: str,
        content: str,
        token_count: int = 0,
    ) -> Message:
        """Append a message to a conversation and update conversation timestamp."""
        msg = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            token_count=token_count,
        )
        db.add(msg)

        # Update conversation updated_at
        stmt = select(Conversation).where(Conversation.id == conversation_id)
        res = await db.execute(stmt)
        conv = res.scalars().first()
        if conv:
            from app.models.conversation import get_utc_now
            conv.updated_at = get_utc_now()

        await db.commit()
        await db.refresh(msg)
        return msg
