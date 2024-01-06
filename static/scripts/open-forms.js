document.addEventListener('DOMContentLoaded', () => {
  const signupForm = document.getElementById('signupForm')
  signupForm.addEventListener('hidden.bs.modal', event => {
    // do something...
  });

  const loginForm = document.getElementById('loginForm')
  loginForm.addEventListener('hidden.bs.modal', event => {
    // do something...
  });
});