class Chat {
	constructor(username, socket) {
		this.username = username;
		this.socket = socket;
		this.conversation = JSON.parse(conversation)[0];
		console.log(this.conversation);

		this.titleElement = document.getElementById('title');
		this.headTitleElement = document.getElementById('head_title');
		this.chatWindow = document.getElementById('chatWindow');
		this.messageInput = document.getElementById('messageInput');
		this.robot_button = document.getElementById('robot_button');
		this.robot_proposition = document.getElementById('robot_proposition');
		this.send_proposition = document.getElementById('send_proposition');

		if (this.conversation.host == this.username) {
			robot_button.style.display = 'block';
		}

		this.verifyAccess();
		this.loadConversation();
		this.initializeEvents();
	}

	verifyAccess() {
		if (this.username !== this.conversation.guest && this.username !== this.conversation.host) {
			sessionStorage.setItem('error', 'Connect before accessing the conversation page');
			window.location.href = '/';
		}
	}

	initializeEvents() {
		this.socket.on('message', (data) => {
			if (data.conversation_id === this.conversation.id) {
				this.displayMessage(data);
			}
		});
		this.socket.on('follow_up', (data) => this.displayRobotMessage(data));
	}

	displayMessage(data) {
		const messageElement = document.createElement('div');
		messageElement.innerHTML = data.user ? `<b><u>${data.user}:</u></b>  ${data.content}` : data.message;
		this.chatWindow.appendChild(messageElement);
	}

	displayRobotMessage(data) {
		console.log('displayRobotMessage', data);
		this.robot_proposition.style.display = 'block';
		this.send_proposition.style.display = 'block';
		this.robot_proposition.innerHTML = data;
	}

	sendMessage(message) {
		console.log('sendMessage', message, this.username);
		if (!message || !this.socket.connected) {
			this.displayMessage({ message: 'Cannot send message, connection is not open' });
			return;
		}

		const data = {
			username: this.username,
			title: this.conversation.title,
			content: message,
		};

		this.socket.emit('message', data);
		this.messageInput.value = '';
	}

	loadConversation() {
		if (this.conversation.messages) {
			this.titleElement.innerHTML =
				`<b>${this.conversation.title}</b>: <br/>` +
				'Host: ' +
				(this.username === this.conversation.host ? `<u>${this.conversation.host}</u>` : this.conversation.host) +
				', Guest: ' +
				(this.username === this.conversation.guest ? `<u>${this.conversation.guest}</u>` : this.conversation.guest);

			this.headTitleElement.innerHTML = this.conversation.title;
			this.chatWindow.innerHTML = '';

			if (Array.isArray(this.conversation.messages)) {
				this.conversation.messages.forEach((message) => this.displayMessage(message));
			}
		}
	}

	handleRobotButton() {
		console.log('handleRobotButton');
		this.ask_follow_up();
	}

	ask_follow_up() {
		console.log('ask_follow_up');
		this.socket.emit('follow_up', this.conversation.title);
	}
}

window.onload = () => {
	const chat = new Chat(sessionStorage.getItem('username'), io('http://localhost:8000'));
	document.getElementById('sendButton').addEventListener('click', (event) => {
		event.preventDefault();
		chat.sendMessage(this.messageInput.value);
	});
	document.getElementById('robot_button').addEventListener('click', (event) => {
		event.preventDefault();
		chat.handleRobotButton();
	});
	document.getElementById('send_proposition').addEventListener('click', (event) => {
		event.preventDefault();
		chat.sendMessage(this.robot_proposition.innerHTML);
	});
};
