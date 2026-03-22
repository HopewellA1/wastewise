
function showToast(message, type="success") {
    const toastEl = document.getElementById('liveToast');
    const toastMessage = document.getElementById('toast-message');

    // Change color
    toastEl.className = `toast align-items-center text-bg-${type} border-0`;

    // Set message
    toastMessage.textContent = message;

    // Show toast
    const toast = new bootstrap.Toast(toastEl);
    toast.show();
  }