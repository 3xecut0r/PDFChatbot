document.addEventListener('DOMContentLoaded', async () => {
    const BASE_URL = 'http://127.0.0.1:8000';
    document.getElementById("payment-btn").addEventListener("click", async function() {
        try {
            const response = await fetch('/users/pay', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
                },
            });
            if (response.ok) {
                const data = await response.json();
                window.location.href = data;
            } else {
                throw new Error('Payment request failed');
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });
    
    
});