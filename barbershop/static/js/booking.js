/* ============================================================
   床山 — Booking interactions
   Everything else (day navigation, modal show/hide, focus
   trapping) is handled by Bootstrap's own JS. This file only
   covers the one thing Bootstrap has no opinion on: the
   running price total on the service-select step.
   ============================================================ */

   document.addEventListener('DOMContentLoaded', () => {
    initServiceTotal();
    initHankoModal();
  });
  
  /* -- Running total on the service-select form -- */
  function initServiceTotal() {
    const form = document.querySelector('[data-service-form]');
    const totalEl = document.querySelector('[data-service-total]');
    if (!form || !totalEl) return;
  
    const checkboxes = form.querySelectorAll('input[type="checkbox"][data-price]');
  
    function updateTotal() {
      let total = 0;
      checkboxes.forEach(cb => {
        if (cb.checked) total += parseFloat(cb.dataset.price || '0');
      });
      totalEl.textContent = `¥${total}`;
    }
  
    checkboxes.forEach(cb => cb.addEventListener('change', updateTotal));
    updateTotal();
  }
  
  /* -- Auto-show the hanko confirmation modal on load --
     Bootstrap's Modal API handles focus trapping, Escape-to-close,
     and backdrop clicks; this just triggers it. */
  function initHankoModal() {
    const el = document.getElementById('hankoModal');
    if (el) new bootstrap.Modal(el).show();
  }