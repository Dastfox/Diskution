class Chat {
	constructor(username, socket) {
		this.username = username;
		this.socket = socket;
		this.conversation = JSON.parse(conversation);
		console.log('Chat constructor', this.username, this.conversation);

		this.socket.on('connect', this.onConnect.bind(this));
		this.socket.on('message', this.onMessage.bind(this));
		this.socket.on('convCreated', this.onConvCreated.bind(this));
		this.socket.onopen = this.onOpen.bind(this);
	}

	displayMessage(user, message) {
		const chatWindow = document.getElementById('chatWindow');
		const messageElement = document.createElement('div');
		messageElement.innerText = user ? `${user}: ${message}` : message;
		chatWindow.appendChild(messageElement);
	}

	sendMessage() {
		console.log('sendMessage');
		const messageInput = document.getElementById('messageInput');
		const message = messageInput.value;

		if (!this.socket.connected) {
			this.displayMessage('Cannot send message, connection is not open');
			return;
		}

		const data = { username: this.username, conversationTitle: title, message: message };
		this.socket.emit('message', data);

		messageInput.value = '';
	}

	switchConversation(conversationSlug) {
		const conversationSelect = document.getElementById('conversationSelect');
		const options = conversationSelect.options;

		for (let i = 0; i < options.length; i++) {
			if (options[i].textContent.includes(conversationSlug)) {
				conversationSelect.selectedIndex = i;
				this.loadConversation(options[i].value);
				break;
			}
		}
	}

	loadConversation(conversationId) {
		const chatWindow = document.getElementById('chatWindow');
		chatWindow.innerHTML = '';
		const messages = this.conversation.messages;
		if (Array.isArray(messages)) {
			messages.forEach((message) => {
				this.displayMessage(message.user, message.content);
			});
		}
	}

	onConnect() {}

	onOpen() {}

	onMessage(data) {
		this.displayMessage(data.user, data.message);
	}
}

document.addEventListener('DOMContentLoaded', function () {
	const username = sessionStorage.getItem('username'); // replace this line with how you want to fetch the username
	const chat = new Chat(username, io('http://localhost:8000'));

	document.getElementById('sendButton').addEventListener('click', function (event) {
		event.preventDefault();
		chat.sendMessage();
	});

	// document.getElementById('conversationSelect').addEventListener('change', function (event) {
	// 	event.preventDefault();
	// 	chat.loadConversation(this.value);
	// });
});
