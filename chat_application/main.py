import json
import socketio
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from chat_application.database import Database
from chat_application.openai_call import get_follow_up_question
from dotenv import load_dotenv
import os
import mysql.connector
from fastapi.middleware.cors import CORSMiddleware

sio = socketio.AsyncServer(async_mode="asgi")
app = FastAPI()
templates = Jinja2Templates(directory="chat_application/Front/templates")
app.mount(
    "/static", StaticFiles(directory="chat_application/Front/static"), name="static"
)
# get env db user and password

origins = [
    "http://localhost:8000",  # adjust to match the origin you're connecting from
    "http://your-app-name.herokuapp.com",  # adjust to match your Heroku app's URL
]

# Attach middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
# Create database instance and setup the database
db_url = os.getenv("DATABASE_URL")
db = Database(db_url)
db.setup()


@app.on_event("shutdown")
def shutdown_event():
    db.close()


@app.get("/", response_class=HTMLResponse)
async def chat_page(request: Request):
    if os.getenv("LOCAL") == "true":
        server_url = "http://localhost:8000"
    else:
        server_url = os.getenv("SERVER_URL")
    print("server_url", server_url)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "server_url": server_url,
        },
    )


@sio.on("message")
async def message(sid, data):
    print("message", data)
    user, _ = db.get_or_create_user_from_username(data["username"])
    conversation = db.get_conversation_by_title(data["title"])
    db.insert_message(
        user, conversation, data["content"]
    )  # Pass the user_id to the insert_message method
    response = {
        "conversation_id": conversation.id,
        "user": data["username"],
        "content": data["content"],
    }
    await sio.emit("message", response)


@sio.on("username_set")
async def username_set(sid, username):
    print("username_set", username)
    if not username or username == "":
        await sio.emit("username error", room=sid)
        return
    user, _ = db.get_or_create_user_from_username(username, create=True)
    if user:
        conversations = db.get_conversations_from_user(username)
        print("username_setaze", conversations)
        if conversations:
            print("loadConversation", conversations)
            await sio.emit(
                "loadConversation",
                db.convert_conversations_to_json(conversations),
                room=sid,
            )


@sio.on("check_username_exists")
async def check_username_exists(sid, username):
    print("check_username_exists", username)
    user = db.get_or_create_user_from_username(username, create=False)
    if user:
        await sio.emit("username_exists", room=sid)
    else:
        await sio.emit("username_does_not_exist", room=sid)


@sio.on("loadConversation")
async def load_conversation(sid, username):
    print("loadConversation", username)
    user, _ = db.get_or_create_user_from_username(username, create=False)
    if user:
        conversations = db.get_conversations_from_user(user.username)
        conversations_json = db.convert_conversations_to_json(conversations)

        with open("conversations.json", "w") as f:
            json.dump(conversations_json, f)
        if conversations:
            await sio.emit(
                "loadConversation",
                conversations_json,
                room=sid,
            )


@sio.on("createConversation")
async def createConversation(sid, guest, host, title):
    print("createConversation", guest, host, title)
    guest, _ = db.get_or_create_user_from_username(guest, create=False)
    host, _ = db.get_or_create_user_from_username(host, create=True)
    if not guest or not host:
        await sio.emit("user_not_found", room=sid)
        return

    db.create_conversation(host.username, guest.username, title)

    return await sio.emit(
        "conversation_created",
        {"guest": guest.username, "host": host.username, "title": title},
        room=sid,
    )


@app.get("/conversation/{title}", response_class=HTMLResponse)
async def conversation_page(request: Request, title: str):
    print("conversation_page", title)
    # Fetch the conversation details from the database using the title
    conversation = db.get_conversation_by_title(title)
    if not conversation:
        # If the conversation does not exist, return a 404 error
        raise HTTPException(status_code=404, detail="Conversation not found")
    conversation_json = db.convert_conversations_to_json([conversation])

    return templates.TemplateResponse(
        "chat.html", {"request": request, "conversation": conversation_json}
    )


@sio.on("follow_up")
async def follow_up(
    sid,
    title,
    pre_prompt=None,
    prompt=None,
    use_default_pre=False,
    use_default_prompt=False,
):
    print("follow_up", title)
    conversation = db.get_conversation_by_title(title)
    if not conversation:
        # If the conversation does not exist, return a 404 error
        raise HTTPException(status_code=404, detail="Conversation not found")
    conversation_json = json.loads(db.convert_conversations_to_json([conversation]))
    messages = conversation_json[0].get("messages", [])
    response = get_follow_up_question(
        json_podcast_transcript=messages,
        pre_prompt=pre_prompt,
        prompt=prompt,
        use_default_pre=use_default_pre,
        use_default_prompt=use_default_prompt,
    )
    return await sio.emit("follow_up", response, room=sid)


app = socketio.ASGIApp(sio, other_asgi_app=app)
