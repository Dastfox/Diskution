// Establish a WebSocket connection
// const socket = new WebSocket('ws://localhost:8000/ws');

// Establish a Socket.IO connection
const socket = io('http://localhost:8000');

// Function to display a message in the chat window
function displayMessage(user, message) {
	const chatWindow = document.getElementById('chatWindow');
	const messageElement = document.createElement('div');
	messageElement.innerText = user ? user + ': ' + message : message;
	chatWindow.appendChild(messageElement);
}

// Function to send a message
function sendMessage() {
	const messageInput = document.getElementById('messageInput');
	const message = messageInput.value;
	const usernameInput = document.getElementById('usernameInput');
	const username = usernameInput.value;
	const data = JSON.stringify({ username: username, message: message });
	if (socket.readyState === WebSocket.OPEN) {
		socket.send(data);
	} else {
		displayMessage('Cannot send message, connection is not open');
	}
	messageInput.value = '';
}

// Event listener for WebSocket connection open
socket.onopen = function () {
	displayMessage(undefined, 'Connected to chat');
};

// Event listener for WebSocket message received
socket.onmessage = function (event) {
	const data = JSON.parse(event.data);
	const message = data.message;
	const user = data.user;
	displayMessage(user, message);
};

// Event listener for form submit
const sendButton = document.getElementById('sendButton');
sendButton.addEventListener('click', function (event) {
	event.preventDefault();
	sendMessage();
});
