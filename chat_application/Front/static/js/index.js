class Index {
	constructor(error) {
		this.selectors = [
			'socket',
			'setUsernameButton',
			'setConversationButton',
			'usernameInput',
			'conversationSelect',
			'usernameError',
			'conversationError',
			'addGuestButton',
			'createConversationButton',
			'guestSelectInput',
			'conversationCreateInput',
			'selectConversationDiv',
			'createConversationDiv',
			'usernameDisplay',
			'error',
		];

		this.initializeSelectors();
		this.initializeEvents();
		error && this.handleError(error);
	}
	initializeSelectors() {
		this.selectors.forEach((selector) => (this[selector] = document.getElementById(selector)));
		this.conversations = [];
		this.socket = io('http://localhost:8000');
	}

	initializeEvents() {
		this.setUsernameButton.addEventListener('click', this.handleSetUsernameButton.bind(this));
		this.setConversationButton.addEventListener('click', this.handleSetConversationButton.bind(this));
		this.addGuestButton.addEventListener('click', this.handleAddGuestButton.bind(this));
		this.createConversationButton.addEventListener('click', this.handleCreateConversationButton.bind(this));
		this.socket.on('loadConversation', this.handleLoadConversations.bind(this));
		this.socket.on('username error', this.handleError.bind(this));
		this.socket.on('conversation error', this.handleError.bind(this));
	}

	handleSetUsernameButton(event) {
		if (this.username) {
			this.usernameInput.style.display = 'inline';
			this.setUsernameButton.textContent = 'Set username';
			this.selectConversationDiv.style.display = 'none';
			this.createConversationDiv.style.display = 'none';
			document.getElementById('usernameDisplay').textContent = ``;
			this.usernameInput.value = '';
			sessionStorage.removeItem('username'); // Remove the username from SessionStorage
			this.username = undefined;
		} else {
			if (!this.usernameInput.value) return;
			event.preventDefault();
			this.conversationError.style.display = 'none';
			const username = this.usernameInput.value;
			this.socket.emit('username_set', username);
			this.createConversationDiv.style.display = 'block';
			this.usernameInput.style.display = 'none';
			this.setUsernameButton.textContent = 'Change Username';
			this.username = username;
			sessionStorage.setItem('username', username); // Save the username to SessionStorage
			this.usernameDisplay.textContent = `Username: ${username}`;
			// Check if there are any conversations to select
		}
	}

	handleSetConversationButton(event) {
		event.preventDefault();
		const conversationName = this.conversationSelect.value;
		// redirect to the conversation page
		window.location.href = `/conversation/${conversationName}`;
	}

	handleAddGuestButton(event) {
		console.log('handleAddGuestButton');
		event.preventDefault();
		const guestName = this.guestSelectInput.value;

		this.socket.emit('check_username_exists', guestName);
		this.guestSelectInput.disabled = true; // Disable the input field temporarily
		this.addGuestButton.textContent = 'Checking...'; // Change the button text

		// Wait for the server response
		if (guestName === this.username) {
			this.error.style.display = 'none';
			console.log('guestName === this.username');
			// guest name is the same as the user's name
			this.guestSelectInput.value = ''; // Reset the input value
			this.guestSelectInput.disabled = false; // Enable the input field
			this.addGuestButton.textContent = 'Add Guest'; // Change the button text
			this.error.style.display = 'block'; // show the error
			this.error.textContent = 'Guest name cannot be the same as your username';
		} else {
			this.error.style.display = 'none'; // hide the error
			this.socket.on('username_exists', () => {
				this.error.style.display = 'none';
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
				error.style.display = 'block';
				error.textContent = 'User does not exist';
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
		conversations = JSON.parse(conversations);

		this.conversations = conversations;
		console.log('handleLoadConversations', this.conversations);
		if (conversations.length != 0) {
			this.selectConversationDiv.style.display = 'block';
		}

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
		console.log('handleMakeConversationButton', this.conversationCreateInput.value, this.guestName, this.username);
		event.preventDefault();
		const conversationName = this.conversationCreateInput.value;
		this.socket.emit('createConversation', this.guestName, this.username, conversationName);
		// redirect to conversation page
		this.socket.on('conversation_created', (data) => {
			console.log('conversation_created', data);
			window.location.href = `/conversation/${conversationName}`;
		});
	}

	handleError(error) {
		this.conversationError.textContent = error;
		this.conversationError.style.display = 'block';
	}
}

document.addEventListener('DOMContentLoaded', function () {
	const error = sessionStorage.getItem('error');
	new Index(error);
});
