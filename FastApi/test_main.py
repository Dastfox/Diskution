import pytest
from fastapi.testclient import TestClient
import socketio

from main import app, sio  # import your app and socketio server


# Client for HTTP tests
@pytest.fixture
def client():
    return TestClient(app)


# Client for SocketIO tests
@pytest.fixture
def sio_client():
    sio_client = socketio.Client()
    sio_client.connect("http://localhost:8000")
    yield sio_client
    sio_client.disconnect()


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_message(sio_client):
    @sio_client.on("message")
    def on_message(data):
        assert data["user"] == "TestUser"
        assert data["message"] == "Hello, World!"

    sio_client.emit("message", {"username": "TestUser", "message": "Hello, World!"})


def test_disconnect(sio_client):
    sio_client.disconnect()
    assert sio_client.eio.state == "disconnected"
