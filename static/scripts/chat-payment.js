document.addEventListener('DOMContentLoaded', async () => {
    const premium = localStorage.getItem('premium');
    const paymentBtn = document.getElementById('payment-btn');

    paymentBtn.addEventListener("click", async function() {
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