class Index {
	constructor() {
		this.socket = io('http://localhost:8000');
		this.setUsernameButton = document.getElementById('setUsernameButton');
		this.setConversationButton = document.getElementById('setConversationButton');
		this.usernameInput = document.getElementById('usernameInput');
		this.conversationSelect = document.getElementById('conversationSelect');
		this.usernameError = document.getElementById('usernameError');
		this.conversationError = document.getElementById('conversationError');
		this.addGuestButton = document.getElementById('addGuestButton');
		this.createConversationButton = document.getElementById('createConversationButton');
		this.guestSelectInput = document.getElementById('guestSelectInput');
		this.conversationNameInput = document.getElementById('conversationCreateInput');
		this.init();
	}

	init() {
		this.setUsernameButton.addEventListener('click', (event) => this.handleSetUsernameButton(event));
		this.setConversationButton.addEventListener('click', (event) => this.handleSetConversationButton(event));
		this.addGuestButton.addEventListener('click', (event) => this.handleAddGuestButton(event));
		this.createConversationButton.addEventListener('click', (event) => this.handleCreateConversationButton(event));
		this.socket.on('loadConversation', (conversations) => this.handleLoadConversations(conversations));
		this.socket.on('username error', (error) => this.handleUsernameError(error));
		this.socket.on('conversation error', (error) => this.handleConversationError(error));
	}
	handleSetUsernameButton(event) {
		if (this.username) {
			this.usernameInput.style.display = 'inline';
			this.setUsernameButton.textContent = 'Set username';
			document.getElementById('createConversationDiv').style.display = 'none';
			document.getElementById('usernameDisplay').textContent = ``;
			this.usernameInput.value = '';
			sessionStorage.removeItem('username'); // Remove the username from SessionStorage
			this.username = undefined;
		} else {
			if (!this.usernameInput.value) return;
			event.preventDefault();
			const username = this.usernameInput.value;
			this.socket.emit('username_set', username);
			document.getElementById('createConversationDiv').style.display = 'block';
			this.usernameInput.style.display = 'none';
			this.setUsernameButton.textContent = 'Change Username';
			this.username = username;
			sessionStorage.setItem('username', username); // Save the username to SessionStorage
			document.getElementById('usernameDisplay').textContent = `Username: ${username}`;
		}
	}

	handleSetConversationButton(event) {
		event.preventDefault();
		const conversationName = this.conversationSelect.value;
		// redirect to the conversation page
		window.location.href = `/conversation/${conversationName}`;
	}

	handleAddGuestButton(event) {
		const gustSameAsUserErrorSpan = document.getElementById('guestSameAsUserError');
		const userDoesNotExistErrorSpan = document.getElementById('guestError');
		console.log('handleAddGuestButton');
		event.preventDefault();
		const guestName = this.guestSelectInput.value;

		this.socket.emit('check_username_exists', guestName);
		this.guestSelectInput.disabled = true; // Disable the input field temporarily
		this.addGuestButton.textContent = 'Checking...'; // Change the button text

		// Wait for the server response
		if (guestName === this.username) {
			userDoesNotExistErrorSpan.style.display = 'none';
			console.log('guestName === this.username');
			// guest name is the same as the user's name
			this.guestSelectInput.value = ''; // Reset the input value
			this.guestSelectInput.disabled = false; // Enable the input field
			this.addGuestButton.textContent = 'Add Guest'; // Change the button text
			gustSameAsUserErrorSpan.style.display = 'block'; // show the error
		} else {
			gustSameAsUserErrorSpan.style.display = 'none'; // hide the error
			this.socket.on('username_exists', () => {
				userDoesNotExistErrorSpan.style.display = 'none';
				// User exists
				console.log('username_exists');
				this.guestSelectInput.style.display = 'none'; // Hide the input field
				this.addGuestButton.textContent = 'Change Guest'; // Change the button text
				this.addGuestButton.removeEventListener('click', this.handleAddGuestButton); // Remove the event listener
				this.addGuestButton.addEventListener('click', (event) => this.handleChangeGuestButton(event)); // Add a new event listener
				document.getElementById('guestNameContainer').textContent = guestName;
				this.createConversationButton.disabled = false;
				this.guestName = guestName;
			});
			this.socket.on('username_does_not_exist', () => {
				userDoesNotExistErrorSpan.style.display = 'block';
				// User does not exist
				console.log('username_does_not_exist');
				this.guestSelectInput.value = ''; // Reset the input value
				this.guestSelectInput.disabled = false; // Enable the input field
				this.addGuestButton.textContent = 'Add Guest'; // Change the button text
			});
		}
	}

	handleChangeGuestButton(event) {
		event.preventDefault();
		this.guestSelectInput.style.display = 'inline'; // Show the input field
		this.addGuestButton.textContent = 'Change Guest'; // Change the button text
		this.guestSelectInput.value = ''; // Reset the input value
		this.guestSelectInput.disabled = false; // Enable the input field
		document.getElementById('guestNameContainer').innerHTML = ''; // Remove the <span> element
		this.addGuestButton.removeEventListener('click', this.handleChangeGuestButton); // Remove the event listener
		this.addGuestButton.addEventListener('click', (event) => this.handleAddGuestButton(event)); // Add the original event listener
	}
	handleLoadConversations(conversations) {
		console.log(conversations);
		conversations = JSON.parse(conversations);
		while (this.conversationSelect.firstChild) {
			this.conversationSelect.removeChild(this.conversationSelect.firstChild);
		}
		conversations.forEach((conversation) => {
			const option = document.createElement('option');
			// assuming the conversation object has a 'name' field that holds the conversation name
			option.value = conversation.title;
			option.textContent = conversation.title;
			this.conversationSelect.appendChild(option);
		});
	}

	handleCreateConversationButton(event) {
		console.log('handleMakeConversationButton', this.conversationNameInput.value, this.guestName, this.username);
		event.preventDefault();
		const conversationName = this.conversationNameInput.value;
		this.socket.emit('createConversation', this.guestName, this.username, conversationName);
		// redirect to conversation page
		// window.location.href = `/conversation/${conversationName}`;
	}

	handleUsernameError(error) {
		this.usernameError.textContent = error;
		this.usernameError.style.display = 'block';
	}

	handleConversationError(error) {
		this.conversationError.textContent = error;
		this.conversationError.style.display = 'block';
	}
}

document.addEventListener('DOMContentLoaded', function () {
	new Index();
});
