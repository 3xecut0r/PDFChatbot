document.addEventListener('DOMContentLoaded', async () => {
    const chatIdDisplay = document.getElementById('chatIdDisplay');
    const messageDisplay = document.getElementById('messageDisplay');
    
    chatIdDisplay.addEventListener('click', async (event) => {
        const clickedElement = event.target;

        if (clickedElement.tagName.toLowerCase() === 'svg' && clickedElement.id === 'deleteChat') {
            const confirmed = confirm(`Are you sure you want to delete this chat?`);
            if (confirmed) {
                const chatLink = clickedElement.parentElement;
                const chatId = chatLink.textContent.replace('Chat #', '').trim();

                try {
                    const response = await fetch(`/chats/${chatId}`, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    });

                    if (response.ok) {
                        chatLink.remove();
                        messageDisplay.innerHTML = '';
                    } else {
                        console.error('Failed to delete chat');
                    }
                } catch (error) {
                    console.error('Error:', error);
                }
            }
        }
    });
});
