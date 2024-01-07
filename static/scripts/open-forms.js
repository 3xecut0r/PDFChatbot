document.addEventListener('DOMContentLoaded', () => {
  const signupForm = document.getElementById('signupForm')
  signupForm.addEventListener('hidden.bs.modal', event => {
    // do something...
  });

  const loginForm = document.getElementById('loginForm')
  loginForm.addEventListener('hidden.bs.modal', event => {
    // do something...
  });

  const selectElement = document.getElementById('aiSelector');

  document.addEventListener('DOMContentLoaded', () => {
    const selectElement = document.getElementById('aiSelector');
    const premiumModal = new bootstrap.Modal(document.getElementById('premiumModal'));

    selectElement.addEventListener('change', (event) => {
        const selectedAI = event.target.value;
        if (selectedAI === 'gpt-3.5-turbo') {
            premiumModal.show(); 
        }
    });
  });

});