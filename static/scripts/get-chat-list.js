document.addEventListener('DOMContentLoaded', async () => {
    const accessToken = localStorage.getItem('accessToken');
    if (!accessToken) {
        window.location.href = '/main/';
    }

    const BASE_URL = 'http://127.0.0.1:8000';

    try {
        const response = await fetch(`${BASE_URL}/chats/user_chats`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const data = await response.json();
            const chatIds = data.chat_ids;
            const chatIdDisplay = document.getElementById('chatIdDisplay');
            chatIds.forEach(chatId => {
                chatIdDisplay.innerHTML += `<div class="chat-link">Chat #${chatId}</div>`;
            });
        } else {
            console.error('Failed to get user chats');
        }
    } catch (error) {
        console.error('Error:', error);
    }

    function checkChats() {
        const chatsExist = localStorage.getItem('chats');
        if (!chatsExist || chatsExist.length === 0) {
            checkchat.innerHTML = `No chats yet...`;
        }
        else {
            checkchat.innerHTML = ``;
        }
    }
    checkChats();
});
