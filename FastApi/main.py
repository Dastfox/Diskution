import json
import sqlite3

import socketio
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

sio = socketio.AsyncServer(async_mode="asgi")
app = FastAPI()
templates = Jinja2Templates(directory="FastApi/Front/templates")
app.mount("/static", StaticFiles(directory="FastApi/Front/static"), name="static")

# Create database connection and cursor
connection = sqlite3.connect("db.sqlite3")
cursor = connection.cursor()

# Create table if it doesn't exist
# Create table if it doesn't exist
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY,
    username TEXT,
    message TEXT NOT NULL
)
"""
)


# @app.get("/", response_class=HTMLResponse)
# async def chat_page(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})


# # TODO recherches socketIo


# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     try:
#         while True:
#             data = await websocket.receive_text()
#             data_dict = json.loads(data)
#             print(data_dict)
#             username = data_dict.get(
#                 "username", "Unknown"
#             )  # use default username if none provided
#             message = data_dict.get("message", "")  # use empty message if none provided
#             cursor.execute(
#                 "INSERT INTO messages (username, message) VALUES (?, ?)",
#                 (
#                     username,
#                     message,
#                 ),
#             )
#             print(username, message)
#             connection.commit()
#             response = json.dumps({"user": username, "message": message})
#             await websocket.send_text(response)
#     except WebSocketDisconnect:
#         # clean data
#         pass


@app.get("/", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@sio.on("connect")
def connect(sid, environ):
    print("connect ", sid)


@sio.on("message")
async def message(sid, data):
    print("message ", data)
    username = data.get("username", "Unknown")
    message = data.get("message", "")
    cursor.execute(
        "INSERT INTO messages (username, message) VALUES (?, ?)",
        (
            username,
            message,
        ),
    )
    connection.commit()
    response = {"user": username, "message": message}
    await sio.emit("message", response, room=sid)


@sio.on("disconnect")
def disconnect(sid):
    print("disconnect ", sid)


app = socketio.ASGIApp(sio, other_asgi_app=app)
