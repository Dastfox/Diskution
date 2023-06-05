import socketio
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from FastApi.database import Database

sio = socketio.AsyncServer(async_mode="asgi")
app = FastAPI()
templates = Jinja2Templates(directory="FastApi/Front/templates")
app.mount("/static", StaticFiles(directory="FastApi/Front/static"), name="static")

# Create database instance and setup the database
db = Database("sqlite:///db.sqlite3")
db.setup()


@app.on_event("shutdown")
def shutdown_event():
    db.close()


@app.get("/", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


@sio.event
async def connect(sid, environ):
    pass


@sio.on("message")
async def message(sid, data):
    user, _ = db.get_or_create_user_from_username(data["username"])
    recipientName = data.get("recipientName", None)
    if recipientName:
        recipient = db.get_or_create_user_from_username(recipientName)
        db.insert_message(user, recipient, data.get("message", ""))
        response = {"user": data["username"], "message": data["message"]}
        await sio.emit("message", response, room=sid)


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
async def loadConversation(sid, username):
    user, _ = db.get_or_create_user_from_username(username, create=False)
    if user:
        conversations = db.get_conversations_from_user(user.username)
        conversations_json = db.convert_conversations_to_json(conversations)
        print("loadConversation", conversations_json)
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
    if not guest:
        await sio.emit("recipient_not_found", room=sid)
        return

    host, _ = db.get_or_create_user_from_username(host, create=True)

    conversation = db.get_conversation_from_users(host.username, guest.username)
    if not conversation:
        db.create_conversation(host.username, guest.username, title)
    return await sio.emit(
        "conversation_created",
        {"guest": guest.username, "host": host.username, "title": title},
        room=sid,
    )
    
@app.get("/conversation/{title}", response_class=HTMLResponse)
async def conversation_page(request: Request, title: str):
    # Fetch the conversation details from the database using the title
    conversation = db.get_conversation_by_title(title)
    if not conversation:
        # If the conversation does not exist, return a 404 error
        raise HTTPException(status_code=404, detail="Conversation not found")
    conversation_json = db.convert_conversations_to_json([conversation])
    print("conversation_json", conversation_json, type(conversation_json), request)
    
    return templates.TemplateResponse("chat.html", {"request": request, "conversation": conversation_json})



app = socketio.ASGIApp(sio, other_asgi_app=app)
