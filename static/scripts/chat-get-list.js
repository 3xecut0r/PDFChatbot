document.addEventListener('DOMContentLoaded', async () => {
    const accessToken = localStorage.getItem('accessToken');
    const icon = '<svg class="btn btn-light send-btn-icon" id="deleteChat" xmlns="http://www.w3.org/2000/svg" width="25" height="25" viewBox="0 0 24 24" fill="none" stroke="#71acef" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>'
    
    if (!accessToken) {
        window.location.href = '/main/';
    }

    
    try {
        const response = await fetch('/chats/user_chats', {
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
            const checkchatIdDisplay = document.getElementById('checkchatIdDisplay');
            checkchatIdDisplay.innerHTML = 'No chats yet...';
            if (chatIds.length > 0) {
                checkchatIdDisplay.innerHTML = '';
            }

            chatIds.forEach(chatId => {
                chatIdDisplay.innerHTML += `<div class="chat-link" id="chat-${chatId}"><b>Chat</b> #${chatId}  ${icon}</div>`;
            });
            Array.from(chatIdDisplay.getElementsByClassName('chat-link')).pop().classList.add('active');
        } else {
            console.error('Failed to get user chats');
        }
    } catch (error) {
        console.error('Error:', error);
    }
});
