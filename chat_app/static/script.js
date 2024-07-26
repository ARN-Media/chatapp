const socket = io();
const messagesDiv = document.getElementById('messages');
const messageInput = document.getElementById('message');
const sendButton = document.getElementById('send');
const roomSelect = document.getElementById('room-select');
const logoutButton = document.getElementById('logout');
const userStatusDiv = document.getElementById('user-status');

function appendMessage(username, message) {
    const messageElem = document.createElement('div');
    messageElem.textContent = `${username}: ${message}`;
    messagesDiv.appendChild(messageElem);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

sendButton.addEventListener('click', () => {
    const message = messageInput.value;
    const room = roomSelect.value;
    if (message) {
        socket.emit('send_message', { message, room });
        messageInput.value = '';
    }
});

roomSelect.addEventListener('change', () => {
    socket.emit('join', { room: roomSelect.value });
});

logoutButton.addEventListener('click', () => {
    fetch('/logout').then(() => window.location.href = '/login');
});

socket.on('receive_message', (data) => {
    appendMessage(data.username, data.message);
});

socket.on('user_joined', (data) => {
    appendMessage('System', `${data.username} has joined the room.`);
});

socket.on('user_left', (data) => {
    appendMessage('System', `${data.username} has left the room.`);
});

socket.on('update_user_status', (data) => {
    userStatusDiv.textContent = `User ${data.username} is now ${data.status}`;
});

// Join the default room
socket.emit('join', { room: roomSelect.value });
