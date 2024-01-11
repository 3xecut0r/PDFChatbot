document.addEventListener('DOMContentLoaded', () => {
    const uploadButton = document.getElementById('upload-btn');
    const fileInput = document.getElementById('fileInput');
    const svgIcon = document.querySelector('#upload-btn svg');
    let currentChatId = '659f4157d05bdd352787a28c';


    if (uploadButton && fileInput) {
        uploadButton.addEventListener('click', function () {
            fileInput.click();
        });

        fileInput.addEventListener('change', function () {
            const selectedFile = fileInput.files[0];
            uploadFile(selectedFile);
        });

        async function uploadFile(file) {
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
});