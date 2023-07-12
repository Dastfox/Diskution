import os
from starlette.testclient import TestClient
import sys
sys.path.append(".")
import socketio
import main
from fastapi import status
client = TestClient(main.app)  # Create a test client instance
sio_client = socketio.Client()  # Create a socketio client instance
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

@pytest.fixture(scope='session')
def test_database():
    # Setup: Create a new database
    engine = create_engine('sqlite:///test_database.db')  # change to your database URL
    Session = scoped_session(sessionmaker(bind=engine))
    main.db.Session = Session  # replace main.db with your database

    yield  # this is where the testing happens

    # Teardown: Delete the test database
    Session.remove()
    os.remove('test_database.db')  # replace with your test database's file path


def test_home_page():
    response = client.get('/')
    assert response.status_code == status.HTTP_200_OK
    
    
    
class TestUsernameSet:
    def setup_method(self, method):
        self.sid = '12345'
        self.username = 'test_host'

    @pytest.mark.asyncio
    async def test_username_set(self):
        with main.db.session_scope() as session:
            await main.username_set(self.sid, self.username)

            user, _ = main.db.get_or_create_user_from_username(self.username)
            session.add(user)
            session.refresh(user)
            print("azfeafzfazfaz",user)
            assert user.username == self.username


class TestConversationCreation:
    def setup_method(self, method):
        self.sid = '12345'
        self.guest_username = 'test_guest'
        self.host_username = 'test_host'
        self.title = 'test_conversation'

    @pytest.mark.asyncio
    async def test_create_conversation(self):
        with main.db.session_scope() as session:
            guest, guest_created = main.db.get_or_create_user_from_username(self.guest_username)
            host, host_created = main.db.get_or_create_user_from_username(self.host_username)
            
            if guest_created:
                session.add(guest)
                session.refresh(guest)
            if host_created:
                session.add(host)
                session.refresh(host)
            session.commit()

            await main.createConversation(self.sid, self.guest_username, self.host_username, self.title)
            print(guest, host, type(guest), type(host))

            conversation = main.db.get_conversation_by_title(self.title)
            assert conversation.title == self.title
            assert conversation.guest_id == guest.id
            assert conversation.host_id == host.id
    
    @pytest.mark.asyncio
    async def test_load_conversation(self):
        with main.db.session_scope() as session:
            main.load_conversation(self.sid, self.guest_username)
            
            conversation = main.db.get_conversation_by_title(self.title)
            assert conversation.title == self.title




class TestFollowUp:
    def setup_method(self, method):
        self.sid = '12345'
        self.title = 'test_conversation'

    @pytest.mark.asyncio
    async def test_follow_up(self):
        await main.follow_up(self.sid, self.title)

        conversation = main.db.get_conversation_by_title(self.title)
        print(conversation)
        assert conversation is not None





def test_conversation_page():
    title = 'test_conversation'
    response = client.get(f'/conversation/{title}')
    assert response.status_code == status.HTTP_200_OK
    # add additional checks related to the conversation page
    

class TestMessage:
    def setup_method(self, method):
        self.sid = '12345'
        self.host = 'test_host'
        self.guest = 'test_guest'
        self.conversation_title = 'test_conversation'
        self.message_content = 'Hello, World!'

    @pytest.mark.asyncio
    async def test_send_and_receive_message(self):
        with main.db.session_scope() as session:
            host, _ = main.db.get_or_create_user_from_username(self.host)
            guest, _ = main.db.get_or_create_user_from_username(self.guest)
            await main.createConversation(self.sid, guest.username, host.username, self.conversation_title)
            

            data = {
                "username": self.host,
                "title": self.conversation_title,
                "content": self.message_content
            }

            await main.message(self.sid, data)

            # Assuming there is a method to get the latest message of a conversation
            conversation = main.db.get_conversation_by_title(self.conversation_title)
            message = main.db.get_messages_by_conv_id(conversation.id)[-1]

            assert message.user_id == host.id
            assert message.conversation_id == conversation.id
            assert message.content == self.message_content
 
        


@pytest.fixture(scope="session", autouse=True)
def cleanup(request):
    """Cleanup a testing session."""
    yield
    with main.db.session_scope() as session:
        
        guest, _ = main.db.get_or_create_user_from_username('test_guest')
        if guest:
            main.db.delete_user(guest)
        
        host, _ = main.db.get_or_create_user_from_username('test_host')
        if host:
            main.db.delete_user(host)        







