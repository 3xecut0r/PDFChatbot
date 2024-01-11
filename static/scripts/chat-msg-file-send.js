document.addEventListener('DOMContentLoaded', () => {
    const uploadButton = document.getElementById('upload-btn');
    const fileInput = document.getElementById('fileInput');
    const svgIcon = document.querySelector('#upload-btn svg');
    
    const createChatButton = document.getElementById('create-chat');
    const sendMsgButton = document.getElementById('send-msg');
    
    const chatDisplay = document.getElementById('messageDisplay');
    const chatIdDisplay = document.getElementById('chatIdDisplay');
    const checkchat = document.getElementById('checkchatIdDisplay');
    
    const inputField = document.getElementById('exampleFormControlTextarea1');
    const deleteChatIcon = '<svg class="btn btn-light send-btn-icon" id="deleteChat" xmlns="http://www.w3.org/2000/svg" width="25" height="25" viewBox="0 0 24 24" fill="none" stroke="#71acef" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>'
    const uploadFileIcon = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#71acef" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 15v4c0 1.1.9 2 2 2h14a2 2 0 0 0 2-2v-4M17 8l-5-5-5 5M12 4.2v10.3"/></svg>'

    const selectModel = 'model_basic';
    localStorage.setItem('selectModel', selectModel);
    const aiSelector = document.getElementById('aiSelector');

    aiSelector.addEventListener('change', (event) => {
        const selectedModel = event.target.value;
        localStorage.setItem('selectModel', selectedModel);
    });

    window.onload = function() {
        const premium = localStorage.getItem('premium');
        if (premium === 'true') {
            aiSelector.value = 'model_premium';
            localStorage.setItem('premium', 'model_premium');
        }
    };

    let currentChatId = '';
    

    createChatButton.addEventListener('click', async () => {
        try {
            const token = localStorage.getItem('accessToken');
            const response = await fetch('/chats/', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });


            const data = await response.json();
            if (response.ok) {
                const chatId = data.chat_id;
                currentChatId = chatId;
                checkchat.innerHTML = '';
                chatDisplay.innerHTML = '';
                chatIdDisplay.innerHTML += `<div class="chat-link" id="chat-${chatId}"><b>Chat</b> #${chatId} ${deleteChatIcon}</div>`;
                currentChat = document.getElementById(`chat-${chatId}`);
                const allChats = document.querySelectorAll('.chat-link');
                allChats.forEach(chat => {
                    chat.classList.remove('active');
                });
                currentChat.classList.add('active');
            } else {
                document.getElementById('chatIdDisplay').innerText = 'Failed to create chat';
            }
        } catch (error) {
            console.error('Error:', error);
            document.getElementById('chatIdDisplay').innerText = 'Internal error occurred. Please try again later.';
        }
    });
    

    if (uploadButton && fileInput) {
        uploadButton.addEventListener('click', function () {
            fileInput.click();
        });
    
        fileInput.addEventListener('change', function () {
            const selectedFile = fileInput.files[0];
            currentChatId = document.getElementsByClassName('chat-link active')[0].id.replace('chat-', '').trim();
            uploadFile(selectedFile, currentChatId);
        });
    
        async function uploadFile(file, currentChatId) {
            try {
                const formData = new FormData();
                formData.append('file', file);
                const response = await fetch(`/files/${currentChatId}/upload`, {
                    method: 'POST',
                    body: formData
                });
    
                const data = await response.json();
                console.log('File uploaded:', data);
                svgIcon.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#20c997" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>';
    
            } catch (error) {
                console.error('Error uploading file:', error);
                svgIcon.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#f4533a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line>';
            }
        }
    } else {
        console.error('Elements not found');
    }

    async function sendMessage(currentChatId) {
        try {
            const token = localStorage.getItem('accessToken');
            const selectModel = localStorage.getItem('selectModel');
            const chatId = currentChatId;
            const message = inputField.value;
            chatDisplay.innerHTML += `<div><b>Me:</b> ${message}</div>`;
            inputField.value = '';

            const response = await fetch(`/chats/${chatId}/${selectModel}/send_question`, {
               
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ question: message, model: selectModel })
            });


            const data = await response.json();
       
            if (response.ok) {
                svgIcon.innerHTML = uploadFileIcon;
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
            currentChatId = document.getElementsByClassName('chat-link active')[0].id.replace('chat-', '').trim();
            console.log(currentChatId);
            sendMessage(currentChatId);
        }
    });

    sendMsgButton.addEventListener('click', async () => {
        try {
            currentChatId = document.getElementsByClassName('chat-link active')[0].id.replace('chat-', '').trim();
            await sendMessage(currentChatId);
        } catch (error) {
            console.error('Error:', error);
            chatDisplay.innerHTML += 'Internal error occurred. Please try again later.';
        }
    });

});