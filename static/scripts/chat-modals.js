document.addEventListener('DOMContentLoaded', function() {
    const aiSelector = document.getElementById('aiSelector');
    aiSelector.addEventListener('change', function() {
        const selectedValue = this.value;
        if (selectedValue === 'gpt-3.5-turbo') {
            const modal = new bootstrap.Modal(document.getElementById('premiumModal'));
            modal.show();
        }
    });

    const closeButton = document.querySelector('#premiumModal .btn-close');
    closeButton.addEventListener('click', function() {
        const modal = bootstrap.Modal.getInstance(document.getElementById('premiumModal'));
        if (modal) {
            modal.hide();
        }
    });
});