document.addEventListener('DOMContentLoaded', () => {
    function logout() {
        localStorage.removeItem('accessToken');
        window.location.href = '/main/'; 
    }

    const logoutButton = document.getElementById('logout');
    if (logoutButton) {
        logoutButton.addEventListener('click', function(event) {
            event.preventDefault();
            logout();
        });
    }
});
