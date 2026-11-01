import pytest
import os
import sys

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import init_db


@pytest.mark.asyncio
async def test_phase2_auth_and_conversations():
    import uuid
    await init_db()
    test_email = f"phase2_{uuid.uuid4().hex[:8]}@example.com"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Register a new user
        reg_resp = await ac.post(
            "/api/v1/auth/register",
            json={
                "email": test_email,
                "username": "phase2tester",
                "password": "Password123!",
            },
        )
        assert reg_resp.status_code == 201
        reg_data = reg_resp.json()
        assert "access_token" in reg_data
        token = reg_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Duplicate registration should fail
        dup_resp = await ac.post(
            "/api/v1/auth/register",
            json={
                "email": test_email,
                "username": "phase2tester",
                "password": "Password123!",
            },
        )
        assert dup_resp.status_code == 400

        # 3. Login
        login_resp = await ac.post(
            "/api/v1/auth/login",
            json={
                "email": test_email,
                "password": "Password123!",
            },
        )
        assert login_resp.status_code == 200
        assert "access_token" in login_resp.json()

        # 4. Get Current User profile (/me)
        me_resp = await ac.get("/api/v1/auth/me", headers=headers)
        assert me_resp.status_code == 200
        assert me_resp.json()["email"] == test_email

        # 5. Create conversation
        conv_resp = await ac.post(
            "/api/v1/conversations",
            headers=headers,
            json={"title": "My First Project Chat", "model": "smart-assistant-v1"},
        )
        assert conv_resp.status_code == 201
        conv_data = conv_resp.json()
        conv_id = conv_data["id"]
        assert conv_data["title"] == "My First Project Chat"

        # 6. List conversations
        list_resp = await ac.get("/api/v1/conversations", headers=headers)
        assert list_resp.status_code == 200
        items = list_resp.json()
        assert len(items) >= 1
        assert any(c["id"] == conv_id for c in items)

        # 7. Update conversation title
        patch_resp = await ac.patch(
            f"/api/v1/conversations/{conv_id}",
            headers=headers,
            json={"title": "Updated Chat Title"},
        )
        assert patch_resp.status_code == 200
        assert patch_resp.json()["title"] == "Updated Chat Title"

        # 8. Check empty messages
        msg_resp = await ac.get(f"/api/v1/conversations/{conv_id}/messages", headers=headers)
        assert msg_resp.status_code == 200
        assert msg_resp.json() == []

        # 9. Delete conversation
        del_resp = await ac.delete(f"/api/v1/conversations/{conv_id}", headers=headers)
        assert del_resp.status_code == 204

        # 10. Verify deleted
        get_deleted = await ac.get(f"/api/v1/conversations/{conv_id}", headers=headers)
        assert get_deleted.status_code == 404
