document.addEventListener('DOMContentLoaded', () => {
    const signUpButton = document.querySelector('.sign-up');
    const signInButton = document.querySelector('.log-in');

    function validateFields(emailField, passwordField, button) {
        if (emailField.value.trim() === '' || passwordField.value.trim() === '') {
            emailField.style.borderColor = 'red';
            passwordField.style.borderColor = 'red';
            button.disabled = true;
        } else {
            emailField.style.borderColor = 'green';
            passwordField.style.borderColor = 'green';
            button.disabled = false;
        }
    }
    
    signUpButton.addEventListener('click', async () => {
        const email = document.getElementById('exampleInputEmail1').value;
        const password = document.getElementById('exampleInputPassword1').value;
        //validateFields(email, password, signUpButton);

        try {
            const response = await fetch('http://127.0.0.1:8000/users/signup', {
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
        //validateFields(email, password, signInButton);

        try {
            const response = await fetch('http://127.0.0.1:8000/users/signin', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `username=${email}&password=${password}`,
            });

            if (response.ok) {
                const data = await response.json();
                console.log('User logged in:', data);
                const receivedToken = data.access_token;
                localStorage.setItem('accessToken', receivedToken);
                window.location.href = '/chats/';
            } else {
                console.error('Failed to log in:', response.statusText);
                alert('Login failed. Please try again.');
            }
        } catch (error) {
            console.error('Error during login:', error);
            alert('Internal error occurred. Please try again later.');
        }
    });
});
