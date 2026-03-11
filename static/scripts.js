document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('.search-form');
    const loadingOverlay = document.querySelector('.loading-overlay');

    if (form) {
        form.addEventListener('submit', () => {
            // Show loading overlay
            loadingOverlay.style.display = 'flex';
        });
    }
});
