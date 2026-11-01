from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user_optional
from app.models.user import User
from app.schemas.chat import ChatStreamRequest, RegenerateRequest
from app.services.chat_service import ChatService
from app.services.llm.factory import LLMFactory

router = APIRouter(prefix="/chat", tags=["Chat & Streaming"])


@router.post("/stream")
async def chat_stream(
    request: ChatStreamRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """
    Stream real-time AI responses using Server-Sent Events (SSE).
    Returns text/event-stream with structured token deltas and session metadata.
    """
    user_id = current_user.id if current_user else None
    generator = ChatService.stream_chat_response(
        db=db,
        request=request,
        user_id=user_id,
    )
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/regenerate")
async def regenerate_stream(
    request: RegenerateRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """
    Regenerate the latest assistant response in an existing conversation session.
    """
    user_id = current_user.id if current_user else None
    generator = ChatService.regenerate_response(
        db=db,
        request=request,
        user_id=user_id,
    )
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


models_router = APIRouter(prefix="/models", tags=["Models"])


@models_router.get("", response_model=List[Dict[str, Any]])
async def list_models():
    """Retrieve catalog of supported LLM models and their operational status."""
    return LLMFactory.list_available_models()
