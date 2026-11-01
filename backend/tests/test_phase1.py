import pytest
import os
import sys

# Ensure backend root is on sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings
from app.core.database import init_db, AsyncSessionLocal
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.core.security import get_password_hash, verify_password, create_access_token, decode_access_token


@pytest.mark.asyncio
async def test_health_check():
    """Verify FastAPI health check endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["app"] == settings.APP_NAME


@pytest.mark.asyncio
async def test_database_init_and_models():
    """Verify database initialization and model operations."""
    import uuid
    await init_db()

    async with AsyncSessionLocal() as session:
        # Create a test user
        hashed = get_password_hash("secret123")
        assert verify_password("secret123", hashed)
        assert not verify_password("wrong", hashed)

        unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        test_user = User(
            email=unique_email,
            username="phase1_tester",
            hashed_password=hashed,
        )
        session.add(test_user)
        await session.commit()
        await session.refresh(test_user)
        assert test_user.id is not None

        # Create a test conversation
        conv = Conversation(
            user_id=test_user.id,
            title="Test Conversation",
            model="smart-assistant-v1",
        )
        session.add(conv)
        await session.commit()
        await session.refresh(conv)
        assert conv.id is not None

        # Create a test message
        msg = Message(
            conversation_id=conv.id,
            role="user",
            content="Hello world!",
        )
        session.add(msg)
        await session.commit()
        await session.refresh(msg)
        assert msg.id is not None
        assert msg.content == "Hello world!"


@pytest.mark.asyncio
async def test_jwt_tokens():
    """Verify JWT token creation and decoding."""
    token = create_access_token(subject="user_123")
    payload = decode_access_token(token)
    assert payload is not None
    assert payload.get("sub") == "user_123"
