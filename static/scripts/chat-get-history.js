document.addEventListener('DOMContentLoaded', async () => {
    const BASE_URL = 'http://127.0.0.1:8000';
    const chatIdDisplay = document.getElementById('chatIdDisplay');
    const messageDisplay = document.getElementById('messageDisplay');

    let currentChatId = '';

    chatIdDisplay.addEventListener('click', async (event) => {
        const clickedChat = event.target;
        if (clickedChat.classList.contains('chat-link')) {
            //currentChatId = document.getElementById(`chat-${chatId}`);
            currentChatId = clickedChat.id.replace('chat-', '').trim();

            const allChats = document.querySelectorAll('.chat-link');
            
            allChats.forEach(chat => {
                chat.style.backgroundColor = ''; 
                chat.classList.remove('active')
            });
            clickedChat.style.backgroundColor = 'rgba(0,0,0,0.1)';
            clickedChat.classList.add('active')
            try {
                const response = await fetch(`${BASE_URL}/chats/${currentChatId}/history`, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
                        'Content-Type': 'application/json'
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    if (data.chat_history) {
                        messageDisplay.innerHTML = '';
                        data.chat_history.forEach(message => {
                            messageDisplay.innerHTML += `<div><b>Me:</b> ${message.question}</div>`;
                            messageDisplay.innerHTML += `<div><b>Bot:</b> ${message.answer}</div>`;
                        });
                    } else {
                        messageDisplay.innerHTML = 'No messages in chat yet.';
                    }
                } else {
                    console.error('Failed to fetch chat history');
                }
                
            } catch (error) {
                console.error('Error:', error);
            }
        }
    });
});