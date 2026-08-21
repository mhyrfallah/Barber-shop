/* ============================================================
   床山 — Booking interactions
   Handles day switching, slot selection, and the hanko
   confirmation stamp. No framework dependency; safe to drop
   into a Django template as-is.
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
  initDayRail();
  initSlotGrid();
  initHankoOverlay();
});

/* -- Day tabs -------------------------------------------------- */
function initDayRail() {
  const rail = document.querySelector('.day-rail');
  if (!rail) return;

  rail.addEventListener('click', (e) => {
    const tab = e.target.closest('.day-tab');
    if (!tab || tab.classList.contains('is-full')) return;

    rail.querySelectorAll('.day-tab').forEach(t => t.classList.remove('is-active'));
    tab.classList.add('is-active');

    // If slots are rendered per-day server-side (Django), this fires
    // a normal navigation. Swap for a fetch() call if you want the
    // slot grid to load without a full page reload.
    const dayUrl = tab.dataset.dayUrl;
    if (dayUrl) {
      window.location.href = dayUrl;
    }
  });
}

/* -- Slot grid --------------------------------------------------- */
function initSlotGrid() {
  const grid = document.querySelector('.slot-grid');
  const summaryTime = document.querySelector('[data-summary="time"]');
  const summaryPrice = document.querySelector('[data-summary="price"]');
  const hiddenSlotInput = document.querySelector('input[name="slot_id"]');
  const submitBtn = document.querySelector('.btn-seal');

  if (!grid) return;

  grid.addEventListener('click', (e) => {
    const slot = e.target.closest('.slot');
    if (!slot || slot.classList.contains('is-booked')) return;

    grid.querySelectorAll('.slot').forEach(s => s.classList.remove('is-selected'));
    slot.classList.add('is-selected');

    if (hiddenSlotInput) hiddenSlotInput.value = slot.dataset.slotId || '';
    if (summaryTime) summaryTime.textContent = slot.dataset.time || slot.querySelector('.time')?.textContent || '';
    if (summaryPrice) summaryPrice.textContent = slot.dataset.price || slot.querySelector('.price')?.textContent || '';
    if (submitBtn) submitBtn.disabled = false;
  });
}

/* -- Hanko confirmation overlay ------------------------------------ */
function initHankoOverlay() {
  const form = document.querySelector('[data-reservation-form]');
  const overlay = document.querySelector('.hanko-overlay');
  if (!form || !overlay) return;

  const closeBtn = overlay.querySelector('.btn-close');

  // Show the stamp once the server confirms the reservation.
  // If you submit via a normal POST + redirect, render the
  // template with a flag (e.g. {% if just_booked %}) and call
  // showHanko() on load instead of on 'submit'.
  form.addEventListener('submit', (e) => {
    if (form.dataset.confirmedInline === 'true') {
      e.preventDefault();
      showHanko(overlay);
    }
    // otherwise let the normal Django POST happen
  });

  closeBtn?.addEventListener('click', () => hideHanko(overlay));
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) hideHanko(overlay);
  });
}

function showHanko(overlay) {
  overlay.classList.add('is-active');
  overlay.setAttribute('aria-hidden', 'false');
}

function hideHanko(overlay) {
  overlay.classList.remove('is-active');
  overlay.setAttribute('aria-hidden', 'true');
}

// Expose for server-rendered "just booked" pages:
// <script>window.addEventListener('DOMContentLoaded', showHankoOnLoad);</script>
function showHankoOnLoad() {
  const overlay = document.querySelector('.hanko-overlay');
  if (overlay) showHanko(overlay);
}
window.showHankoOnLoad = showHankoOnLoad;
