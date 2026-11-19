/**
 * CampusConnect — Client-side Interactivity
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Mobile Navigation Toggle
  const mobileToggle = document.getElementById('mobileToggle');
  const navLinks = document.getElementById('navLinks');

  if (mobileToggle && navLinks) {
    mobileToggle.addEventListener('click', () => {
      navLinks.classList.toggle('active');
      const isExpanded = navLinks.classList.contains('active');
      mobileToggle.setAttribute('aria-expanded', isExpanded);
    });
  }

  // 2. Alert Dismissal
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    const closeBtn = alert.querySelector('.alert-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-10px)';
        setTimeout(() => alert.remove(), 250);
      });
    }

    // Auto dismiss after 6 seconds for success/info alerts
    if (alert.classList.contains('alert-success') || alert.classList.contains('alert-info')) {
      setTimeout(() => {
        if (alert.parentElement) {
          alert.style.opacity = '0';
          alert.style.transform = 'translateY(-10px)';
          setTimeout(() => alert.remove(), 250);
        }
      }, 6000);
    }
  });

  // 3. Generic Action Confirmation Modal Handler
  window.openConfirmModal = function(title, message, formId) {
    const modal = document.getElementById('confirmModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalMessage = document.getElementById('modalMessage');
    const confirmBtn = document.getElementById('modalConfirmBtn');

    if (!modal) return;

    if (modalTitle) modalTitle.textContent = title;
    if (modalMessage) modalMessage.textContent = message;

    modal.classList.add('active');

    // On confirm, trigger target form submission
    const handleConfirm = () => {
      const targetForm = document.getElementById(formId);
      if (targetForm) {
        targetForm.submit();
      }
      closeConfirmModal();
    };

    confirmBtn.onclick = handleConfirm;
  };

  window.closeConfirmModal = function() {
    const modal = document.getElementById('confirmModal');
    if (modal) {
      modal.classList.remove('active');
    }
  };

  // Close modal when clicking on backdrop
  const modal = document.getElementById('confirmModal');
  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        closeConfirmModal();
      }
    });
  }
});
