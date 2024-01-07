document.addEventListener('DOMContentLoaded', () => {
    const BASE_URL = 'http://127.0.0.1:8000'; // Замініть на свою адресу сервера
    const createChatButton = document.getElementById('create-chat');
    const sendMsgButton = document.getElementById('send-msg');
    const chatHistoryButton = document.getElementById('chat-history');
    const chatDisplay = document.getElementById('messageDisplay');
    const chatIdDisplay = document.getElementById('chatIdDisplay');
    const checkchat = document.getElementById('checkchatIdDisplay');
    const inputField = document.getElementById('exampleFormControlTextarea1');

    async function sendMessage() {
        try {
            const token = localStorage.getItem('accessToken');
            const chatId = 'your_chat_id';
            const message = inputField.value;
            chatDisplay.innerHTML += `<div><b>Me:</b> ${message}</div>`;
            inputField.value = '';
            const response = await fetch(`${BASE_URL}/chats/${chatId}/send_question`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ question: message })
            });

            const data = await response.json();
            if (response.ok) {
                const answer = data.answer;
                chatDisplay.innerHTML += `<div><b>Chat:</b> ${answer}</div>`;
            } else {
                document.getElementById('messageDisplay').innerText = 'Failed to send message';
            }
        } catch (error) {
            console.error('Error:', error);
            chatDisplay.innerHTML += 'Internal error occurred. Please try again later.';
        }
    }

    inputField.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            sendMessage();
        }
    });

    
    createChatButton.addEventListener('click', async () => {
        try {
            const token = localStorage.getItem('accessToken');
            const response = await fetch(`${BASE_URL}/chats/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();
            if (response.ok) {
                const chatId = data.chat_id;
                checkchat.innerHTML = ``;
                chatIdDisplay.innerHTML += `<div class="chat-link">Chat #${chatId}</div>`;
            } else {
                document.getElementById('chatIdDisplay').innerText = 'Failed to create chat';
            }
        } catch (error) {
            console.error('Error:', error);
            document.getElementById('chatIdDisplay').innerText = 'Internal error occurred. Please try again later.';
        }
    });

    sendMsgButton.addEventListener('click', async () => {
        try {
            const token = localStorage.getItem('accessToken');
            const chatId = 'your_chat_id';
            const message = document.getElementById('exampleFormControlTextarea1').value;
            chatDisplay.innerHTML += `<div><b>Me:</b> ${message}</div>`;
            document.getElementById('exampleFormControlTextarea1').value = '';
            const response = await fetch(`${BASE_URL}/chats/${chatId}/send_question`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ question: message })
                
            });

            const data = await response.json();
            if (response.ok) {
                const answer = data.answer;
                
                chatDisplay.innerHTML += `<div><b>Chat:</b> ${answer}</div>`;
            } else {
                document.getElementById('messageDisplay').innerText = 'Failed to send message';
            }
        } catch (error) {
            console.error('Error:', error);
            chatDisplay.innerHTML += 'Internal error occurred. Please try again later.';
        }
    });

    chatHistoryButton.addEventListener('click', async () => {
        try {
            const token = localStorage.getItem('accessToken');
            const chatId = 'your_chat_id';

            const response = await fetch(`${BASE_URL}/chats/${chatId}/history`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                }
            });

            const data = await response.json();
            if (response.ok) {
                const chatHistory = data.chat_history;
                document.getElementById('historyDisplay').innerText = `Chat history retrieved successfully! History: ${chatHistory}`;
            } else {
                document.getElementById('historyDisplay').innerText = 'Failed to get chat history';
            }
        } catch (error) {
            console.error('Error:', error);
            document.getElementById('historyDisplay').innerText = 'Internal error occurred. Please try again later.';
        }
    });
});
