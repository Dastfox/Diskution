import pytest
import socketio
from fastapi.testclient import TestClient
from chat_application.main import app, sio


# This is an async fixture that creates a TestClient instance.
@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sio_client():
    return socketio.Client()


# Test FastAPI endpoint
@pytest.mark.asyncio
async def test_chat_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Diskution" in response.text
