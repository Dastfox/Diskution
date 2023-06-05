import inspect
import json
from typing import List
from sqlalchemy import Table, create_engine, Column, Integer, String, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import aliased
from sqlalchemy import or_


Base = declarative_base()


# Association table for many-to-many relationship between User and Conversation
user_conversation = Table(
    "user_conversation",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("conversation_id", Integer, ForeignKey("conversations.id")),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    conversations = relationship(
        "Conversation",
        secondary=user_conversation,
        backref="users",
    )
    messages = relationship("Message", back_populates="user")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    host_id = Column(Integer, ForeignKey("users.id"))
    guest_id = Column(Integer, ForeignKey("users.id"))

    host = relationship("User", foreign_keys=[host_id], backref="hosted_conversations")
    guest = relationship(
        "User", foreign_keys=[guest_id], backref="guested_conversations"
    )
    messages = relationship("Message", back_populates="conversation")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    user = relationship("User", back_populates="messages")
    conversation = relationship("Conversation", back_populates="messages")
    timestamp = Column(Integer, nullable=False)


class Database:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)

    def setup(self):
        Base.metadata.create_all(bind=self.engine)

    def close(self):
        self.engine.dispose()

    def get_or_create_user_from_username(self, username, create=True):
        print("get_or_create_user", username)
        created = False
        with self.Session() as session:
            user = session.query(User).filter(User.username == username).first()

            if not user and not create:
                return

            if not user and create:
                user = User(username=username)
                session.add(user)
                session.commit()
                created = True

            return user, created

    def create_conversation(self, host, guest, title):
        with self.Session() as session:
            # Check if the conversation already exists
            existing_conv = (
                session.query(Conversation)
                .filter(
                    Conversation.host.has(User.username == host),
                    Conversation.guest.has(User.username == guest),
                    Conversation.title == title,
                )
                .first()
            )
            if existing_conv:
                return existing_conv

            # Check if the users exist
            host_obj, _ = self.get_or_create_user_from_username(host)
            guest_obj, _ = self.get_or_create_user_from_username(guest)

            if not host_obj or not guest_obj:
                raise Exception("User does not exist")

            # Create a new conversation
            conv = Conversation()
            conv.guest = guest_obj
            conv.host = host_obj
            conv.title = title

            session.add(conv)
            session.commit()
            print("Created conversation", conv.id)

            return conv

    def insert_message(self, user: User, conversation_id, content):
        with self.Session() as session:
            # Check if conversation between user and recipient already exists
            conv = (
                session.query(Conversation)
                .join(user_conversation)
                .filter(Conversation.id == conversation_id)
            )

            msg = Message(
                content=content,
                user_id=user.id,
                conversation_id=conv.id,
                timestamp=func.now(),
            )
            session.add(msg)
            session.commit()

            return conv

    def get_conversations(self):
        with self.Session() as session:
            users = session.query(User).all()  # Get all users
            conversations = {}
            for user in users:
                # For each user get all conversations
                user_conversations = (
                    session.query(Conversation)
                    .join(
                        user_conversation,
                        user_conversation.c.conversation_id == Conversation.id,
                    )
                    .join(User, user_conversation.c.user_id == User.id)
                    .filter(User.id == user.id)
                    .all()
                )

                conversations[user.username] = []
                for conv in user_conversations:
                    messages = [
                        {"message_id": msg.id, "content": msg.content}
                        for msg in conv.messages
                    ]
                    conversations[user.username].append(
                        {"conversation_id": conv.id, "messages": messages}
                    )
            return conversations

    def get_conversations_from_user(self, username):
        with self.Session() as session:
            user_conversations = (
                session.query(Conversation)
                .options(joinedload(Conversation.messages), joinedload(Conversation.guest), joinedload(Conversation.host))  # Eager load messages and users
                .filter(or_(Conversation.host.has(User.username == username), 
                            Conversation.guest.has(User.username == username)))  # Filter by the username column
                .all()
            )
            return user_conversations


    def convert_conversations_to_json(self, conversations):
        results = []
        with self.Session() as session:
            for conv in conversations:
                conv_with_messages = (
                    session.query(Conversation)
                    .options(joinedload(Conversation.messages), joinedload(Conversation.guest), joinedload(Conversation.host))     
                    .filter(Conversation.id == conv.id)
                    .first()
                )
                messages = [
                    {"user": message.user.username, "content": message.content}
                    for message in conv_with_messages.messages
                ]
                result = {
                    "id": conv_with_messages.id,
                    "title": conv_with_messages.title,
                    "guest": conv_with_messages.guest.username,
                    "host": conv_with_messages.host.username,
                    "messages": messages,
                }
                results.append(result)
        return json.dumps(results)

    def get_conversation_by_title(self, title):
        with self.Session() as session:
            conversation = session.query(Conversation).filter(Conversation.title == title).first()
            return conversation
