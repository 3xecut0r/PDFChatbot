document.addEventListener('DOMContentLoaded', function() {
    const aiSelector = document.getElementById('aiSelector');
    const premiumStatus = localStorage.getItem('premium');
    const closeButton = document.querySelector('#premiumModal .btn-close');
    const modal = new bootstrap.Modal(document.getElementById('premiumModal'));
    
    aiSelector.addEventListener('change', function() {
        const selectedValue = this.value;
        if (premiumStatus === 'false' && selectedValue === 'model_premium') {
            modal.show();
        }
    });
    
    closeButton.addEventListener('click', function() {
        if (modal) {
            if (premiumStatus === 'false') {
                aiSelector.value = 'model_basic';
                localStorage.setItem('selectModel', aiSelector.value);
            }
            modal.hide();
        }
    });

    document.addEventListener('click', function (event) {
        var modal = document.getElementById('premiumModal');
        var modalContent = document.querySelector('.modal-content');
        if (event.target === modal || event.target === modalContent) {
            if (premiumStatus === 'false') {
                aiSelector.value = 'model_basic';
                localStorage.setItem('selectModel', aiSelector.value);
            }
        }
    });
});