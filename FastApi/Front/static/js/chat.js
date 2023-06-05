// Establish a Socket.IO connection
const socket = io('http://localhost:8000');
let username = ''; // Initialize the username variable

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

	// Check if the socket is connected
	if (socket.connected) {
		const data = { username: username, message: message };
		socket.emit('message', data); // Emit a 'message' event to the server
	} else {
		displayMessage('Cannot send message, connection is not open');
	}

	messageInput.value = '';
}

// Event listener for Socket.IO connection established
socket.on('connect', function () {});

// Event listener for Socket.IO message received
socket.on('message', function (data) {
	const message = data.message;
	const user = data.user;
	displayMessage(user, message);
});

// Event listener for form submit
const sendButton = document.getElementById('sendButton');
sendButton.addEventListener('click', function (event) {
	event.preventDefault();
	sendMessage();
});

socket.on('initialMessages', function (messages) {
	messages.forEach(function (data) {
		const message = data.message;
		const user = data.user;
		displayMessage(user, message);
	});
});

// Event listener for WebSocket connection open
socket.onopen = function () {
	displayMessage(undefined, 'Connected to chat');

	// Load initial messages
	initialMessages.forEach(function (data) {
		const message = data.message;
		const user = data.user;
		displayMessage(user, message);
	});
};

// Function to set the username
function setUsername() {
	const usernameInput = document.getElementById('usernameInput');
	username = usernameInput.value;
	if (username) {
		// Display the username in the chat window
		const usernameDisplay = document.getElementById('usernameDisplay');
		usernameDisplay.innerText = 'Username: ' + username;

		// Hide the input field and display the "Change Username" button
		usernameInput.style.display = 'none';
		setUsernameButton.style.display = 'none';
		changeUsernameButton.style.display = 'block';
	}
}
// Function to set the username
function setUsername() {
	const usernameInput = document.getElementById('usernameInput');
	username = usernameInput.value;
	if (username) {
		// Display the username in the chat window
		const usernameDisplay = document.getElementById('usernameDisplay');
		usernameDisplay.innerText = 'Username: ' + username;
		usernameDisplay.style.display = 'inline';

		// Hide the input field and display the "Change Username" button
		usernameInput.style.display = 'none';
		setUsernameButton.style.display = 'none';
		changeUsernameButton.style.display = 'inline';
	}
}

// Event listener for "Set Username" button
const setUsernameButton = document.getElementById('setUsernameButton');
setUsernameButton.addEventListener('click', function (event) {
	event.preventDefault();
	setUsername();
});

// Function to change the username
function changeUsername() {
	// Clear the current username
	username = '';

	// Show the input field and display the "Set Username" button
	const usernameInput = document.getElementById('usernameInput');
	usernameInput.value = '';
	usernameInput.style.display = 'inline';
	setUsernameButton.style.display = 'inline';
	changeUsernameButton.style.display = 'none';

	// Clear the username display in the chat window
	const usernameDisplay = document.getElementById('usernameDisplay');
	usernameDisplay.innerText = '';
	usernameDisplay.style.display = 'none';
}

// Event listener for "Change Username" button
const changeUsernameButton = document.getElementById('changeUsernameButton');
changeUsernameButton.addEventListener('click', function (event) {
	event.preventDefault();
	changeUsername();
});
