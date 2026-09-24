/* ============================================================
   MSH Barbershop — Booking interactions
   ============================================================ */

   document.addEventListener('DOMContentLoaded', () => {
    initServiceTotal();
    initConfirmModal();
    initMobileNav();
    initServiceScroll();
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
  
  /* -- Confirmation modal (vanilla) -- */
  function initConfirmModal() {
    const modal = document.getElementById('confirmModal');
    const backdrop = document.getElementById('confirmBackdrop');
    if (!modal || !backdrop) return;
  
    const closeButtons = modal.querySelectorAll('[data-modal-close]');
    let lastFocused = null;
  
    function openModal() {
      lastFocused = document.activeElement;
      modal.classList.add('is-open');
      backdrop.classList.add('is-open');
      backdrop.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
      const closeBtn = modal.querySelector('[data-modal-close]');
      if (closeBtn) closeBtn.focus();
    }
  
    function closeModal() {
      modal.classList.remove('is-open');
      backdrop.classList.remove('is-open');
      backdrop.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
      if (lastFocused && typeof lastFocused.focus === 'function') {
        lastFocused.focus();
      }
    }
  
    closeButtons.forEach(btn => btn.addEventListener('click', closeModal));
    backdrop.addEventListener('click', closeModal);
  
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && modal.classList.contains('is-open')) {
        closeModal();
      }
    });
  }
  
  /* -- Mobile nav toggle -- */
  function initMobileNav() {
    const toggle = document.querySelector('[data-nav-toggle]');
    const panel = document.getElementById('mobileNav');
    if (!toggle || !panel) return;
  
    toggle.addEventListener('click', () => {
      const isOpen = panel.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', String(isOpen));
    });
  }
  
  /* -- Services carousel arrows -- */
  function initServiceScroll() {
    const track = document.querySelector('[data-service-scroll]');
    const prevBtn = document.querySelector('[data-scroll-prev]');
    const nextBtn = document.querySelector('[data-scroll-next]');
    if (!track || !prevBtn || !nextBtn) return;
  
    const step = () => track.clientWidth * 0.6;
  
    prevBtn.addEventListener('click', () => track.scrollBy({ left: -step(), behavior: 'smooth' }));
    nextBtn.addEventListener('click', () => track.scrollBy({ left: step(), behavior: 'smooth' }));
  }