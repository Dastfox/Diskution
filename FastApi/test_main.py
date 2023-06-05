import pytest
from starlette.testclient import TestClient
from fastapi import FastAPI
from main import app, connect, message
from unittest import mock
from unittest.mock import AsyncMock
from main import app, Database
import socketio

client = TestClient(app)

db = Database(":memory:")


# Database setup for the tests
def setup_module():
    db.setup()


def test_app_get():
    response = client.get("/")
    assert response.status_code == 200


@mock.patch("main.sio", autospec=True)
@pytest.mark.asyncio
async def test_connect(mock_sio):
    mock_sio.emit = AsyncMock(return_value=True)
    sid = "123"
    environ = {}
    await connect(sid, environ)
    mock_sio.emit.assert_called_once()


@mock.patch("main.Database.insert_message", autospec=True)
@pytest.mark.asyncio
async def test_message(mock_insert_message):
    sio = socketio.AsyncServer(async_mode="asgi")
    sid = "123"
    data = {"username": "test", "message": "test_message"}
    mock_insert_message.return_value = True
    # Await the async message function, not the mocked insert_message methods
    await message(sid, data)
    mock_insert_message.assert_called_once()


@mock.patch("main.Database.get_messages", autospec=True)
def test_get_messages(mock_get_messages):
    mock_get_messages.return_value = [{"user": "test", "message": "test_message"}]
    result = db.get_messages()
    assert result == [{"user": "test", "message": "test_message"}]


@mock.patch("main.Database.close", autospec=True)
def test_shutdown_event(mock_close):
    with client:
        response = client.get("/")
        assert response.status_code == 200
    mock_close.assert_called_once()
