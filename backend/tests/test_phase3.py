import pytest
import os
import sys
import json

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings
from app.core.database import init_db
from app.services.llm.factory import LLMFactory


@pytest.mark.asyncio
async def test_phase3_models_and_streaming():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Models catalog
        models_resp = await ac.get("/api/v1/models")
        assert models_resp.status_code == 200
        models_data = models_resp.json()
        assert len(models_data) >= 1
        assert any(m["id"] == "smart-assistant-v1" for m in models_data)
        assert LLMFactory.get_provider_name_for_model("smart-assistant-v1") == "mock"
        configured_models = [
            model for model in models_data
            if model["provider"] == settings.DEFAULT_LLM_PROVIDER
        ]
        if settings.DEFAULT_LLM_PROVIDER != "mock":
            assert configured_models[0]["id"] == settings.DEFAULT_MODEL
            assert configured_models[0]["is_active"] is True

        # 2. Chat streaming (New conversation auto-creation)
        stream_payload = {
            "content": "Hello! How can you help me build a modern web app?",
            "model": "smart-assistant-v1",
        }

        conversation_id = None
        tokens_received = []
        events_received = []

        async with ac.stream("POST", "/api/v1/chat/stream", json=stream_payload) as response:
            assert response.status_code == 200
            assert "text/event-stream" in response.headers.get("content-type", "")

            current_event = None
            async for line in response.aiter_lines():
                line = line.strip()
                if not line:
                    continue
                if line.startswith("event:"):
                    current_event = line.replace("event:", "").strip()
                    events_received.append(current_event)
                elif line.startswith("data:"):
                    data_str = line.replace("data:", "").strip()
                    parsed = json.loads(data_str)
                    if current_event == "session":
                        conversation_id = parsed.get("conversation_id")
                    elif current_event == "token":
                        tokens_received.append(parsed.get("delta", ""))

        assert conversation_id is not None
        assert len(tokens_received) > 0
        full_text = "".join(tokens_received)
        assert len(full_text) > 10
        assert "session" in events_received
        assert "token" in events_received
        assert "done" in events_received

        # 3. Verify messages are persisted in DB
        history_resp = await ac.get(f"/api/v1/conversations/{conversation_id}/messages")
        assert history_resp.status_code == 200
        history_data = history_resp.json()
        assert len(history_data) == 2  # 1 user + 1 assistant
        assert history_data[0]["role"] == "user"
        assert history_data[0]["content"] == stream_payload["content"]
        assert history_data[1]["role"] == "assistant"
        assert len(history_data[1]["content"]) > 0

        # 4. Follow-up query in same conversation
        followup_payload = {
            "conversation_id": conversation_id,
            "content": "Can you provide some python code for that?",
            "model": "smart-assistant-v1",
        }
        tokens_followup = []
        async with ac.stream("POST", "/api/v1/chat/stream", json=followup_payload) as response:
            assert response.status_code == 200
            current_event = None
            async for line in response.aiter_lines():
                line = line.strip()
                if line.startswith("event:"):
                    current_event = line.replace("event:", "").strip()
                elif line.startswith("data:"):
                    data_str = line.replace("data:", "").strip()
                    parsed = json.loads(data_str)
                    if current_event == "token":
                        tokens_followup.append(parsed.get("delta", ""))

        assert len(tokens_followup) > 0
        # History should now have 4 messages
        history_resp2 = await ac.get(f"/api/v1/conversations/{conversation_id}/messages")
        assert len(history_resp2.json()) == 4

        # 5. Test Regeneration
        regen_payload = {
            "conversation_id": conversation_id,
            "model": "smart-assistant-v1",
        }
        regen_tokens = []
        async with ac.stream("POST", "/api/v1/chat/regenerate", json=regen_payload) as response:
            assert response.status_code == 200
            current_event = None
            async for line in response.aiter_lines():
                line = line.strip()
                if line.startswith("event:"):
                    current_event = line.replace("event:", "").strip()
                elif line.startswith("data:"):
                    data_str = line.replace("data:", "").strip()
                    parsed = json.loads(data_str)
                    if current_event == "token":
                        regen_tokens.append(parsed.get("delta", ""))

        assert len(regen_tokens) > 0
        # After regeneration of the 4th message, count should still be 4
        history_resp3 = await ac.get(f"/api/v1/conversations/{conversation_id}/messages")
        assert len(history_resp3.json()) == 4
