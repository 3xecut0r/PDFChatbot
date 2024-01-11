document.addEventListener('DOMContentLoaded', () => {
    const signUpButton = document.querySelector('.sign-up');
    const signInButton = document.querySelector('.log-in');

    signUpButton.addEventListener('click', async () => {
        const email = document.getElementById('exampleInputEmail1').value;
        const password = document.getElementById('exampleInputPassword1').value;
        
        if (!email || !password) {
            if (!email) {
                setInvalidFieldStyle('exampleInputEmail1');
            }
            if (!password) {
                setInvalidFieldStyle('exampleInputPassword1');
            }
            return;
        }

        try {
            const response = await fetch('/users/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username: email, password: password }),
            });

            if (response.ok) {
                const data = await response.json();
                console.log('User created:', data);
                window.location.href = '/chats/';
            } else {
                console.error('Failed to sign up:', response.statusText);
                alert('Registration failed. Please try again.');
            }
        } catch (error) {
            console.error('Error during sign up:', error);
            alert('Internal error occurred. Please try again later.');
        }
    });

    signInButton.addEventListener('click', async () => {
        const email = document.getElementById('exampleInputEmail2').value;
        const password = document.getElementById('exampleInputPassword2').value;
        
        if (!email || !password) {
            if (!email) {
                setInvalidFieldStyle('exampleInputEmail2');
            }
            if (!password) {
                setInvalidFieldStyle('exampleInputPassword2');
            }
            return;
        }

        try {
            const response = await fetch('/users/signin', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `username=${email}&password=${password}`,
            });

            if (response.ok) {
                const data = await response.json();
                const receivedToken = data.access_token;
                const premiumStatus = data.premium || false;

                localStorage.setItem('accessToken', receivedToken);
                localStorage.setItem('premium', premiumStatus);
                
                window.location.href = '/chats/';
            } else {
                alert('Login failed. Check your data and try again.');
            }
        } catch (error) {
            console.error('Error during login:', error);
            alert('Internal error occurred. Please try again later.');
        }
    });

    function setInvalidFieldStyle(fieldId) {
        const field = document.getElementById(fieldId);
        field.style.borderColor = 'red';
        field.addEventListener('input', () => {
            if (field.value) {
                field.style.borderColor = ''; 
            }
        });
    }
});
