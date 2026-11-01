from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user_optional
from app.models.user import User
from app.schemas.conversation import ConversationCreate, ConversationUpdate, ConversationResponse
from app.schemas.chat import MessageResponse
from app.services.conversation_service import ConversationService

router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.get("", response_model=List[ConversationResponse])
async def list_conversations(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """List conversations for current user or anonymous guest session."""
    user_id = current_user.id if current_user else None
    return await ConversationService.list_conversations(
        db=db,
        user_id=user_id,
        limit=limit,
        offset=offset,
        search=search,
    )


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    data: ConversationCreate,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """Create a new chat conversation session."""
    user_id = current_user.id if current_user else None
    conv = await ConversationService.create_conversation(db=db, user_id=user_id, data=data)
    return ConversationResponse(
        id=conv.id,
        user_id=conv.user_id,
        title=conv.title,
        model=conv.model,
        system_prompt=conv.system_prompt,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        message_count=0,
    )


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve details for a single conversation session."""
    user_id = current_user.id if current_user else None
    conv = await ConversationService.get_conversation(db, conversation_id, user_id)
    # count messages
    messages = await ConversationService.get_messages(db, conversation_id)
    return ConversationResponse(
        id=conv.id,
        user_id=conv.user_id,
        title=conv.title,
        model=conv.model,
        system_prompt=conv.system_prompt,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        message_count=len(messages),
    )


@router.patch("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: str,
    data: ConversationUpdate,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """Update conversation title or parameters."""
    user_id = current_user.id if current_user else None
    conv = await ConversationService.update_conversation(db, conversation_id, data, user_id)
    messages = await ConversationService.get_messages(db, conversation_id)
    return ConversationResponse(
        id=conv.id,
        user_id=conv.user_id,
        title=conv.title,
        model=conv.model,
        system_prompt=conv.system_prompt,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        message_count=len(messages),
    )


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """Delete a conversation session and its message history."""
    user_id = current_user.id if current_user else None
    await ConversationService.delete_conversation(db, conversation_id, user_id)


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    limit: int = Query(100, ge=1, le=500),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve message history for a conversation session."""
    user_id = current_user.id if current_user else None
    # Validate access
    await ConversationService.get_conversation(db, conversation_id, user_id)
    return await ConversationService.get_messages(db, conversation_id, limit=limit)
