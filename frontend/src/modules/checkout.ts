/**
 * Checkout module - handles multi-step checkout flow
 */

import { api, analytics } from './shared';

interface CheckoutConfig {
  taxRates: Record<string, { rate: number; label: string }>;
  shippingMethods: Array<{ method: string; label: string; base_cost: number }>;
}

interface CheckoutTotals {
  subtotal: number;
  tax: number;
  shipping: number;
  discount: number;
  total: number;
  taxRate: number;
}

interface CartItem {
  productId: number;
  productName: string;
  quantity: number;
  price: number;
}

const state = {
  currentStep: 1,
  cart: [] as CartItem[],
  shipping: { method: 'economy', cost: 5.0 },
  address: {} as Record<string, string>,
  payment: { method: 'card' },
  totals: { subtotal: 0, tax: 0, shipping: 5.0, discount: 0, total: 0, taxRate: 0 } as CheckoutTotals,
  coupon: null as { code: string; discount: number; type: string } | null,
  config: { taxRates: {}, shippingMethods: [], loaded: false } as CheckoutConfig & { loaded: boolean }
};

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-CA', { style: 'currency', currency: 'CAD' }).format(amount);
}

function validatePostalCode(code: string): boolean {
  return /^[A-Z]\d[A-Z]\s?\d[A-Z]\d$/i.test(code);
}

function getProvinceFromPostalCode(code: string): string | null {
  const map: Record<string, string> = {
    A: 'NL', B: 'NS', C: 'PE', E: 'NB', G: 'QC', H: 'QC', J: 'QC',
    K: 'ON', L: 'ON', M: 'ON', N: 'ON', P: 'ON', R: 'MB', S: 'SK',
    T: 'AB', V: 'BC', X: 'NT', Y: 'YT', Z: 'NU'
  };
  return map[code.charAt(0).toUpperCase()] || null;
}

async function loadConfig(): Promise<void> {
  try {
    const [taxes, shipping] = await Promise.all([
      api.get('/api/checkout/taxes/'),
      api.get('/api/checkout/shipping-zones/')
    ]);
    if (taxes.ok && taxes.body.success) state.config.taxRates = taxes.body.provinces;
    if (shipping.ok && shipping.body.success) {
      state.config.shippingMethods = shipping.body.shipping_zones;
      if (state.config.shippingMethods.length > 0) {
        state.shipping.method = state.config.shippingMethods[0].method;
        state.shipping.cost = state.config.shippingMethods[0].base_cost;
      }
    }
    state.config.loaded = true;
  } catch (err) {
    console.error('Failed to load checkout config:', err);
  }
}

function calculateSubtotal(): number {
  const stored = localStorage.getItem('packaxis_cart');
  if (!stored) return 0;
  const items: CartItem[] = JSON.parse(stored);
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

function calculateTax(subtotal: number, province: string | null): number {
  if (!province || !state.config.taxRates[province]) return 0;
  const rate = state.config.taxRates[province].rate;
  state.totals.taxRate = rate;
  return subtotal * rate;
}

function calculateDiscount(subtotal: number): number {
  if (!state.coupon) return 0;
  return state.coupon.type === 'percentage' ? subtotal * state.coupon.discount : state.coupon.discount;
}

function calculateTotals(province?: string | null): CheckoutTotals {
  const subtotal = calculateSubtotal();
  const discount = calculateDiscount(subtotal);
  const discounted = subtotal - discount;
  if (!province) {
    const postal = (document.getElementById('postal_code') as HTMLInputElement)?.value;
    if (postal && validatePostalCode(postal)) province = getProvinceFromPostalCode(postal);
  }
  const tax = calculateTax(discounted, province || null);
  const shipping = state.shipping.cost;
  const total = discounted + tax + shipping;
  state.totals = { subtotal, tax, shipping, discount, total, taxRate: state.config.taxRates[province || '']?.rate || 0 };
  updateSummaryUI();
  return state.totals;
}

function updateSummaryUI(): void {
  const t = state.totals;
  const postal = (document.getElementById('postal_code') as HTMLInputElement)?.value || '';
  const province = getProvinceFromPostalCode(postal);
  const taxLabel = state.config.taxRates[province || '']?.label || 'Tax';

  const set = (id: string, val: string) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  };
  set('summary-subtotal', formatCurrency(t.subtotal));
  set('summary-tax', formatCurrency(t.tax));
  set('tax-label', `${taxLabel} (${(t.taxRate * 100).toFixed(0)}%)`);
  set('summary-shipping', formatCurrency(t.shipping));
  set('summary-total', formatCurrency(t.total));

  const discountRow = document.getElementById('discount-row');
  if (t.discount > 0) {
    discountRow?.classList.remove('hidden');
    set('summary-discount', `-${formatCurrency(t.discount)}`);
    set('discount-label', state.coupon ? `Discount (${state.coupon.code})` : 'Discount');
  } else {
    discountRow?.classList.add('hidden');
  }

  updateCartSummary();
}

function updateCartSummary(): void {
  const stored = localStorage.getItem('packaxis_cart');
  if (!stored) return;
  const items: CartItem[] = JSON.parse(stored);
  const container = document.getElementById('summary-items');
  if (container) {
    container.innerHTML = items
      .map(
        (item) => `
      <div class="flex justify-between text-sm">
        <span class="text-gray-700">${item.productName}</span>
        <span class="text-gray-900 font-medium">${item.quantity}x ${formatCurrency(item.price)}</span>
      </div>
    `
      )
      .join('');
  }
}

function goToStep(step: number): void {
  state.currentStep = step;
  for (let i = 1; i <= 4; i++) {
    const el = document.getElementById(`step-${i}`);
    el?.classList.toggle('hidden', i !== step);
  }
  analytics.track('checkout_step', { step });
}

function validateShippingForm(): void {
  const form = document.getElementById('shipping-form') as HTMLFormElement;
  if (!form || !form.checkValidity()) {
    alert('Please fill in all required fields');
    return;
  }
  const postalInput = document.getElementById('postal_code') as HTMLInputElement;
  const postal = postalInput?.value || '';
  if (!validatePostalCode(postal)) {
    showPostalCodeError('Invalid postal code. Use format A1A 1A1');
    return;
  }
  state.address = {
    first_name: (document.getElementById('first_name') as HTMLInputElement)?.value || '',
    last_name: (document.getElementById('last_name') as HTMLInputElement)?.value || '',
    email: (document.getElementById('email') as HTMLInputElement)?.value || '',
    phone: (document.getElementById('phone') as HTMLInputElement)?.value || '',
    street_address: (document.getElementById('street_address') as HTMLInputElement)?.value || '',
    street_address_2: (document.getElementById('street_address_2') as HTMLInputElement)?.value || '',
    city: (document.getElementById('city') as HTMLInputElement)?.value || '',
    province: (document.getElementById('province') as HTMLInputElement)?.value || '',
    postal_code: postal
  };
  calculateTotals(state.address.province);
  goToStep(3);
}

function showPostalCodeError(msg: string): void {
  const el = document.getElementById('postal-validation');
  if (el) {
    el.classList.remove('hidden');
    el.innerHTML = `<span class="text-red-600">✗ ${msg}</span>`;
  }
}

function showPostalCodeValid(): void {
  const el = document.getElementById('postal-validation');
  if (el) {
    el.classList.remove('hidden');
    el.innerHTML = '<span class="text-green-600">✓ Valid postal code</span>';
  }
}

function debounce<T extends (...args: any[]) => void>(fn: T, ms = 300): T {
  let timer: number;
  return ((...args: any[]) => {
    clearTimeout(timer);
    timer = window.setTimeout(() => fn(...args), ms);
  }) as T;
}

const handlePostalChange = debounce(() => {
  const input = document.getElementById('postal_code') as HTMLInputElement;
  const postal = input?.value.toUpperCase();
  if (!postal) {
    showPostalCodeError('Postal code required');
    return;
  }
  if (!validatePostalCode(postal)) {
    showPostalCodeError('Invalid format. Use: A1A 1A1');
    return;
  }
  const province = getProvinceFromPostalCode(postal);
  if (!province) {
    showPostalCodeError('Unable to identify province');
    return;
  }
  showPostalCodeValid();
  calculateTotals(province);
});

async function validateCoupon(code: string): Promise<{ success: boolean; error?: string }> {
  const resp = await api.post('/api/checkout/calculate/', {
    coupon_code: code,
    items: JSON.parse(localStorage.getItem('packaxis_cart') || '[]'),
    postal_code: (document.getElementById('postal_code') as HTMLInputElement)?.value || 'M5V 3A8',
    shipping_method: state.shipping.method
  });
  if (resp.ok && resp.body.success && resp.body.discount > 0) {
    state.coupon = { code, discount: resp.body.discount, type: 'fixed' };
    calculateTotals();
    return { success: true };
  }
  return { success: false, error: resp.body.errors?.[0] || 'Invalid coupon' };
}

function applyCoupon(): void {
  const input = document.getElementById('coupon_code') as HTMLInputElement;
  const code = input?.value.trim();
  if (!code) return;
  validateCoupon(code).then((result) => {
    const msg = document.getElementById('coupon-message');
    if (result.success) {
      if (msg) {
        msg.classList.remove('hidden', 'text-red-600');
        msg.classList.add('text-green-600');
        msg.textContent = '✓ Coupon applied';
      }
    } else {
      if (msg) {
        msg.classList.remove('hidden', 'text-green-600');
        msg.classList.add('text-red-600');
        msg.textContent = result.error || 'Invalid coupon';
      }
    }
  });
}

async function submitOrder(): Promise<void> {
  analytics.track('checkout_submit');
  const cart = JSON.parse(localStorage.getItem('packaxis_cart') || '[]');
  const payload = {
    address: state.address,
    cart,
    shipping: state.shipping,
    payment: state.payment,
    coupon: state.coupon
  };
  const resp = await api.post('/api/orders/', payload);
  if (resp.ok && resp.body.success) {
    localStorage.removeItem('packaxis_cart');
    window.location.href = resp.body.redirect_url || `/orders/${resp.body.order_id}/`;
  } else {
    alert(resp.body.error || 'Order submission failed. Please try again.');
  }
}

export function initCheckout(): void {
  if (!document.getElementById('checkout-page')) return;
  loadConfig().then(() => calculateTotals());

  document.getElementById('postal_code')?.addEventListener('input', handlePostalChange);
  document.getElementById('btn-continue-shipping')?.addEventListener('click', validateShippingForm);
  document.getElementById('btn-apply-coupon')?.addEventListener('click', applyCoupon);
  document.getElementById('btn-submit-order')?.addEventListener('click', submitOrder);

  document.querySelectorAll('[data-step]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const step = parseInt(btn.getAttribute('data-step') || '1', 10);
      goToStep(step);
    });
  });
}
