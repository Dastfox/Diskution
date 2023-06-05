import mock
import pytest
import socketio
from starlette.testclient import TestClient
from main import app, connect, message
from main import app
from database import Database

import pytest
from starlette.testclient import TestClient
from unittest.mock import patch
from main import (
    app,
    connect,
    message,
    username_set,
    loadConversation,
    recipient_set,
)

client = TestClient(app)

db = Database("sqlite:///:memory:")


def setup_module():
    db.setup()


def test_app_get():
    response = client.get("/")
    assert response.status_code == 200


@patch("main.sio", autospec=True)
@pytest.mark.asyncio
async def test_connect(mock_sio):
    sid = "123"
    environ = {}
    await connect(sid, environ)
    mock_sio.emit.assert_not_called()  # no emit in connect function


@patch("main.Database.get_or_create_user_from_username", return_value="test")
@patch("main.Database.insert_message", return_value=True)
@pytest.mark.asyncio
async def test_message(mock_insert_message, mock_get_or_create_user_from_username):
    sid = "123"
    data = {"username": "test", "message": "test_message", "recipientName": "recipient"}
    await message(sid, data)
    mock_insert_message.assert_called_once()


@mock.patch("main.Database.get_conversations_from_user", autospec=True)
@pytest.mark.asyncio
async def test_username_set(mock_get_user):
    sio = socketio.AsyncServer(async_mode="asgi")
    mock_get_user.return_value = []
    sid = "123"
    username = "test"
    await username_set(sid, username)
    mock_get_user.assert_called_once_with(db, username)


@mock.patch("main.Database.get_conversations_from_user", autospec=True)
@pytest.mark.asyncio
async def test_loadConversation(mock_get_user):
    sio = socketio.AsyncServer(async_mode="asgi")
    mock_get_user.return_value = []
    sid = "123"
    username = "test"
    await loadConversation(sid, username)
    mock_get_user.assert_called_once_with(db, username)


@mock.patch("main.Database.get_conversation_from_users", autospec=True)
@mock.patch("main.Database.get_or_create_user_from_username", autospec=True)
@pytest.mark.asyncio
async def test_recipient_set(mock_get_or_create_user, mock_get_conversation):
    sio = socketio.AsyncServer(async_mode="asgi")
    user = mock.MagicMock()
    user.username = "test"
    mock_get_or_create_user.return_value = user
    sid = "123"
    recipientName = "test"
    username = "test"
    await recipient_set(sid, recipientName, username)
    mock_get_or_create_user.assert_called()
    mock_get_conversation.assert_called()
