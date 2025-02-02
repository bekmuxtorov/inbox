let chatSocket = null;
let pendingMessages = new Set();

function formatTime(date) {
    return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
}

async function initializeWebSocket() {
    try {
        const response = await fetch('http://127.0.0.1:8000/chat/tickets/create/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                subject: "New Ticket",
                ticket_uuid: uuidv4()
            })
        });

        if (!response.ok) {
            throw new Error("Failed to create ticket");
        }

        const ticketData = await response.json();
        const ticketUUID = ticketData.ticket_uuid;

        chatSocket = new WebSocket(`ws://127.0.0.1:8000/ws/chat/${ticketUUID}/`);

        chatSocket.onmessage = function (e) {
            const data = JSON.parse(e.data);
            if (!pendingMessages.has(data.message)) {
                appendMessage(data.message, false, new Date());
            } else {
                pendingMessages.delete(data.message);
            }
        };

        chatSocket.onclose = function (e) {
            if (!e.wasClean) {
                console.error('Socket unexpected closing');
            }
        };

    } catch (error) {
        console.error("Error initializing WebSocket:", error);
    }
}

function uuidv4() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'
        .replace(/[xy]/g, function (c) {
            const r = Math.random() * 16 | 0,
                v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
}

function sendMessage() {
    if (!chatSocket || chatSocket.readyState !== WebSocket.OPEN) return;

    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    const timestamp = new Date();

    if (message) {
        pendingMessages.add(message);
        chatSocket.send(JSON.stringify({ 'message': message, 'time': timestamp }));
        appendMessage(message, true, timestamp);
        input.value = '';
    }
}

function toggleChat() {
    const chatContainer = document.getElementById('chatContainer');
    const chatButton = document.querySelector('.start-chat-btn');
    const chatMessages = document.getElementById('chatMessages');

    if (chatContainer.classList.contains('active')) {
        chatContainer.classList.remove('active');
        chatButton.textContent = 'Start Chat';

        chatMessages.innerHTML = '';

        if (chatSocket) {
            chatSocket.close();
        }
    } else {
        initializeWebSocket();
        chatContainer.classList.add('active');
        chatButton.textContent = 'Close Chat';
        document.getElementById('messageInput').focus();
    }
}

function appendMessage(message, isOwnMessage, timestamp) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageElement = document.createElement('div');

    messageElement.className = isOwnMessage ? 'own-message' : 'other-message';
    messageElement.style.textAlign = isOwnMessage ? 'right' : 'left';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.textContent = message;

    const timeElement = document.createElement('span');
    timeElement.className = 'message-time';
    timeElement.textContent = formatTime(timestamp);

    bubble.appendChild(timeElement);
    messageElement.appendChild(bubble);
    messagesContainer.appendChild(messageElement);

    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

window.addEventListener('beforeunload', function () {
    if (chatSocket) {
        chatSocket.close();
    }
});

document.getElementById('messageInput').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        sendMessage();
    }
});
