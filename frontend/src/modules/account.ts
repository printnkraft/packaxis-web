/**
 * Account module - handles account dashboard functionality
 */

import { api, analytics } from './shared';

function initOrderTracking(): void {
  const trackBtns = document.querySelectorAll('[data-track-order]');
  trackBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      const orderId = btn.getAttribute('data-track-order');
      if (orderId) {
        analytics.track('track_order', { order_id: orderId });
        window.location.href = `/orders/${orderId}/`;
      }
    });
  });
}

function initProfileEdit(): void {
  const form = document.getElementById('profile-form') as HTMLFormElement;
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    const resp = await api.post('/api/accounts/profile/', data);
    if (resp.ok && resp.body.success) {
      showMessage('profile-message', 'Profile updated successfully', 'success');
    } else {
      showMessage('profile-message', resp.body.error || 'Update failed', 'error');
    }
  });
}

function showMessage(containerId: string, text: string, type: 'success' | 'error'): void {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.classList.remove('hidden', 'text-green-600', 'text-red-600');
  el.classList.add(type === 'success' ? 'text-green-600' : 'text-red-600');
  el.textContent = type === 'success' ? `✓ ${text}` : `✗ ${text}`;
  setTimeout(() => el.classList.add('hidden'), 5000);
}

export function initAccount(): void {
  if (!document.getElementById('account-page')) return;
  initOrderTracking();
  initProfileEdit();
  analytics.track('account_dashboard_view');
}
