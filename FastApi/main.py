import json
import sqlite3

import socketio
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


class Database:
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()

    def setup(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                username TEXT,
                message TEXT NOT NULL
            )
            """
        )
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()

    def insert_message(self, username, message):
        self.cursor.execute(
            "INSERT INTO messages (username, message) VALUES (?, ?)",
            (username, message),
        )
        self.connection.commit()

    def get_messages(self):
        self.cursor.execute("SELECT username, message FROM messages")
        rows = self.cursor.fetchall()
        messages = []
        for row in rows:
            username, message = row
            message_data = {"user": username, "message": message}
            messages.append(message_data)
        return messages


sio = socketio.AsyncServer(async_mode="asgi")
app = FastAPI()
templates = Jinja2Templates(directory="FastApi/Front/templates")
app.mount("/static", StaticFiles(directory="FastApi/Front/static"), name="static")

# Create database instance and setup the database
db = Database("db.sqlite3")
db.setup()


@app.on_event("shutdown")
def shutdown_event():
    db.close()


@app.get("/", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@sio.event
async def connect(sid, environ):
    print("Connected", sid)
    messages = db.get_messages()
    await sio.emit("initialMessages", messages, room=sid)


@sio.on("message")
async def message(sid, data):
    print("message ", data)
    username = data.get("username", "Unknown")
    message = data.get("message", "")
    db.insert_message(username, message)
    response = {"user": username, "message": message}
    await sio.emit("message", response, room=sid)


app = socketio.ASGIApp(sio, other_asgi_app=app)
