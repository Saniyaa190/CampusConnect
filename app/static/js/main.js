/**
 * CampusConnect Client-Side Script
 */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize Bootstrap Tooltips
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Auto-dismiss Flash Alerts after 5 seconds
  const autoDismissAlerts = document.querySelectorAll('.alert-dismissible');
  autoDismissAlerts.forEach(alert => {
    setTimeout(() => {
      try {
        const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
        bsAlert.close();
      } catch (e) {
        // Ignored if already closed
      }
    }, 5000);
  });

  // Image Preview on File Input Change
  const imageInput = document.getElementById('image');
  const imagePreviewContainer = document.getElementById('image-preview-container');
  const imagePreview = document.getElementById('image-preview');

  if (imageInput && imagePreview && imagePreviewContainer) {
    imageInput.addEventListener('change', function () {
      const file = this.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
          imagePreview.src = e.target.result;
          imagePreviewContainer.classList.remove('d-none');
        };
        reader.readAsDataURL(file);
      } else {
        imagePreviewContainer.classList.add('d-none');
      }
    });
  }

  // Registration Confirm Dialog
  const registerForms = document.querySelectorAll('.form-confirm-register');
  registerForms.forEach(form => {
    form.addEventListener('submit', function (e) {
      if (!confirm('Are you sure you want to register for this event? Make sure you meet eligibility requirements.')) {
        e.preventDefault();
      }
    });
  });

  // Cancellation Confirm Dialog
  const cancelForms = document.querySelectorAll('.form-confirm-cancel');
  cancelForms.forEach(form => {
    form.addEventListener('submit', function (e) {
      if (!confirm('Are you sure you want to cancel your registration? Your seat will be made available to other students.')) {
        e.preventDefault();
      }
    });
  });
});
