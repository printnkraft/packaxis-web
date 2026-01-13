/**
 * PackAxis Enterprise Checkout
 * Production-ready checkout experience with premium UX
 */

(function() {
  'use strict';

  // ==========================================================================
  // STATE
  // ==========================================================================

  const State = {
    step: 1,
    maxSteps: 5,
    cart: [],
    shipping: { method: null, cost: 0, label: '', days: '' },
    coupon: null,
    totals: { subtotal: 0, discount: 0, shipping: 0, tax: 0, total: 0 },
    config: { taxRates: {}, shippingZones: [] },
    addresses: [],
    processing: false,
    order: null
  };

  // ==========================================================================
  // UTILITIES
  // ==========================================================================

  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

  function formatCurrency(amount) {
    return new Intl.NumberFormat('en-CA', { 
      style: 'currency', 
      currency: 'CAD',
      minimumFractionDigits: 2 
    }).format(amount);
  }

  function formatDate(date) {
    return new Intl.DateTimeFormat('en-CA', { 
      month: 'long', 
      day: 'numeric', 
      year: 'numeric' 
    }).format(date);
  }

  function formatTime(date) {
    return new Intl.DateTimeFormat('en-CA', { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    }).format(date);
  }

  function formatShortDate(date) {
    return new Intl.DateTimeFormat('en-CA', { 
      month: 'short', 
      day: 'numeric' 
    }).format(date);
  }

  function getCSRF() {
    const cookie = document.cookie.split('; ').find(r => r.startsWith('csrftoken='));
    return cookie ? cookie.split('=')[1] : '';
  }

  async function api(url, options = {}) {
    try {
      const res = await fetch(url, {
        headers: { 
          'Content-Type': 'application/json', 
          'X-CSRFToken': getCSRF() 
        },
        ...options
      });
      const data = await res.json();
      return { ok: res.ok, data };
    } catch (e) {
      console.error('API Error:', e);
      return { ok: false, data: null, error: e.message };
    }
  }

  function setVal(id, value) {
    const el = document.getElementById(id);
    if (el) el.value = value || '';
  }

  function getVal(id) {
    return document.getElementById(id)?.value?.trim() || '';
  }

  // ==========================================================================
  // ENTERPRISE TOAST NOTIFICATIONS - Premium Design System
  // ==========================================================================

  const toastQueue = [];
  let isProcessingQueue = false;

  function createToastContainer() {
    let container = $('.toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container';
      container.setAttribute('role', 'alert');
      container.setAttribute('aria-live', 'polite');
      container.setAttribute('aria-atomic', 'false');
      document.body.appendChild(container);
    }
    return container;
  }

  function showToast(type, title, message, duration = 4000) {
    const container = createToastContainer();
    
    // Limit concurrent toasts for clean UX
    const existingToasts = container.querySelectorAll('.toast:not(.toast--exiting)');
    if (existingToasts.length >= 3) {
      // Dismiss oldest toast
      dismissToast(existingToasts[0]);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast--${type}`;
    toast.style.setProperty('--toast-duration', `${duration}ms`);
    
    // Premium icon mapping with better semantic icons
    const icons = {
      success: 'check_circle',
      error: 'error',
      warning: 'warning',
      info: 'info'
    };

    // Sanitize content to prevent XSS
    const sanitize = (str) => {
      const div = document.createElement('div');
      div.textContent = str;
      return div.innerHTML;
    };

    toast.innerHTML = `
      <span class="toast__icon" aria-hidden="true">
        <span class="material-symbols-rounded">${icons[type] || 'info'}</span>
      </span>
      <div class="toast__content">
        <div class="toast__title">${sanitize(title)}</div>
        ${message ? `<div class="toast__message">${sanitize(message)}</div>` : ''}
      </div>
      <button class="toast__close" aria-label="Dismiss notification" type="button">
        <span class="material-symbols-rounded">close</span>
      </button>
    `;

    container.appendChild(toast);

    // Pause progress on hover
    let timeoutId;
    let remainingTime = duration;
    let startTime = Date.now();

    const startTimer = () => {
      startTime = Date.now();
      if (remainingTime > 0) {
        timeoutId = setTimeout(() => dismissToast(toast), remainingTime);
      }
    };

    const pauseTimer = () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
        remainingTime -= Date.now() - startTime;
      }
    };

    toast.addEventListener('mouseenter', pauseTimer);
    toast.addEventListener('mouseleave', startTimer);

    // Close button handler
    const closeBtn = toast.querySelector('.toast__close');
    closeBtn.addEventListener('click', () => {
      if (timeoutId) clearTimeout(timeoutId);
      dismissToast(toast);
    });

    // Start auto-dismiss timer
    if (duration > 0) {
      startTimer();
    }

    // Announce to screen readers
    announceToScreenReader(`${type}: ${title}. ${message || ''}`);

    return toast;
  }

  function dismissToast(toast) {
    if (!toast || toast.classList.contains('toast--exiting')) return;
    
    toast.classList.add('toast--exiting');
    
    // Clean removal after animation
    setTimeout(() => {
      toast.remove();
      
      // Clean up container if empty
      const container = $('.toast-container');
      if (container && container.children.length === 0) {
        // Keep container for future toasts
      }
    }, 350);
  }

  // Screen reader announcement helper
  function announceToScreenReader(message) {
    const announcement = document.createElement('div');
    announcement.setAttribute('role', 'status');
    announcement.setAttribute('aria-live', 'polite');
    announcement.setAttribute('aria-atomic', 'true');
    announcement.className = 'sr-only';
    announcement.style.cssText = 'position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);border:0;';
    announcement.textContent = message;
    document.body.appendChild(announcement);
    setTimeout(() => announcement.remove(), 1000);
  }

  // ==========================================================================
  // LOADING STATES
  // ==========================================================================

  function setButtonLoading(btn, loading) {
    if (!btn) return;
    if (loading) {
      btn.disabled = true;
      btn.classList.add('btn--loading');
      btn.dataset.originalText = btn.innerHTML;
      const icon = btn.querySelector('.material-symbols-rounded');
      if (icon) icon.style.visibility = 'hidden';
    } else {
      btn.disabled = false;
      btn.classList.remove('btn--loading');
      if (btn.dataset.originalText) {
        btn.innerHTML = btn.dataset.originalText;
        delete btn.dataset.originalText;
      }
    }
  }

  // ==========================================================================
  // CART
  // ==========================================================================

  function loadCart() {
    try {
      State.cart = JSON.parse(localStorage.getItem('packaxis_cart') || '[]');
    } catch {
      State.cart = [];
    }
  }

  function saveCart() {
    localStorage.setItem('packaxis_cart', JSON.stringify(State.cart));
    window.dispatchEvent(new CustomEvent('cart:updated', { 
      detail: { count: State.cart.reduce((sum, i) => sum + i.quantity, 0) } 
    }));
  }

  function renderCart() {
    const container = $('#cart-items');
    const empty = $('#cart-empty');
    const countEl = $('#cart-count');
    const continueBtn = $('#cart-continue');

    if (!container) return;

    const totalItems = State.cart.reduce((sum, i) => sum + i.quantity, 0);
    
    if (countEl) {
      countEl.textContent = `${totalItems} item${totalItems !== 1 ? 's' : ''}`;
    }

    if (State.cart.length === 0) {
      container.innerHTML = '';
      if (empty) empty.hidden = false;
      if (continueBtn) continueBtn.disabled = true;
      return;
    }

    if (empty) empty.hidden = true;
    if (continueBtn) continueBtn.disabled = false;

    container.innerHTML = State.cart.map((item, index) => `
      <div class="cart-item" data-index="${index}">
        <div class="cart-item__image">
          ${item.image 
            ? `<img src="${item.image}" alt="${item.productName}">` 
            : '<span class="material-symbols-rounded" style="font-size:2rem;color:#ccc;">inventory_2</span>'
          }
        </div>
        <div class="cart-item__details">
          <div class="cart-item__name">${item.productName}</div>
          ${item.variant ? `<div class="cart-item__variant">${item.variant}</div>` : ''}
          ${item.sku ? `<div class="cart-item__sku">SKU: ${item.sku}</div>` : ''}
        </div>
        <div class="cart-item__quantity">
          <button type="button" class="cart-item__qty-btn" data-action="decrease" data-index="${index}">−</button>
          <span class="cart-item__qty-value">${item.quantity}</span>
          <button type="button" class="cart-item__qty-btn" data-action="increase" data-index="${index}">+</button>
        </div>
        <div class="cart-item__price">
          ${formatCurrency(item.price * item.quantity)}
          <div class="cart-item__unit-price">${formatCurrency(item.price)} each</div>
        </div>
        <button type="button" class="cart-item__remove" data-action="remove" data-index="${index}">
          <span class="material-symbols-rounded">close</span>
        </button>
      </div>
    `).join('');

    // Attach event listeners
    $$('[data-action]', container).forEach(btn => {
      btn.addEventListener('click', handleCartAction);
    });
  }

  function handleCartAction(e) {
    const btn = e.currentTarget;
    const action = btn.dataset.action;
    const index = parseInt(btn.dataset.index);

    if (index < 0 || index >= State.cart.length) return;

    switch (action) {
      case 'increase':
        State.cart[index].quantity++;
        break;
      case 'decrease':
        if (State.cart[index].quantity > 1) {
          State.cart[index].quantity--;
        } else {
          State.cart.splice(index, 1);
        }
        break;
      case 'remove':
        State.cart.splice(index, 1);
        break;
    }

    saveCart();
    renderCart();
    calculateTotals();
    renderSidebarItems();
  }

  function renderSidebarItems() {
    const containers = $$('.order-summary__items');
    
    containers.forEach(container => {
      if (!container || State.cart.length === 0) {
        if (container) container.innerHTML = '';
        return;
      }

      container.innerHTML = State.cart.map(item => `
        <div class="order-summary__item">
          <div class="order-summary__item-image">
            ${item.image 
              ? `<img src="${item.image}" alt="${item.productName}">` 
              : '<span class="material-symbols-rounded" style="font-size:1.25rem;color:#ccc;">inventory_2</span>'
            }
          </div>
          <div class="order-summary__item-details">
            <div class="order-summary__item-name">${item.productName}</div>
            <div class="order-summary__item-qty">Qty: ${item.quantity}</div>
          </div>
          <div class="order-summary__item-price">${formatCurrency(item.price * item.quantity)}</div>
        </div>
      `).join('');
    });
  }

  // ==========================================================================
  // TOTALS (Optimized with debouncing and caching)
  // ==========================================================================

  // Tax rate cache for instant lookups
  const taxCache = new Map();
  let calculateTotalsTimeout = null;

  function calculateTotals() {
    // Debounce rapid calls for better performance
    if (calculateTotalsTimeout) {
      clearTimeout(calculateTotalsTimeout);
    }
    calculateTotalsTimeout = setTimeout(calculateTotalsImmediate, 30);
  }

  function calculateTotalsImmediate() {
    const subtotal = State.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    
    let discount = 0;
    if (State.coupon) {
      discount = State.coupon.type === 'percentage' 
        ? subtotal * (State.coupon.discount / 100) 
        : Math.min(State.coupon.discount, subtotal);
    }

    const province = getVal('ship_province');
    
    // Use cached tax rate for instant calculation
    let taxRate = taxCache.get(province);
    if (taxRate === undefined) {
      taxRate = State.config.taxRates[province]?.rate || 0;
      if (province) taxCache.set(province, taxRate);
    }
    
    const taxableAmount = subtotal - discount;
    const tax = Math.round(taxableAmount * taxRate * 100) / 100; // Round to 2 decimals
    const shipping = State.shipping.cost || 0;
    const total = taxableAmount + tax + shipping;

    State.totals = { subtotal, discount, shipping, tax, total };
    updateTotalsUI();
  }

  function updateTotalsUI() {
    const { subtotal, discount, shipping, tax, total } = State.totals;

    // Step 1 specific
    const summarySubtotal = $('#summary-subtotal');
    const summaryDiscount = $('#summary-discount');
    const discountRow = $('#discount-row');
    const summaryShipping = $('#summary-shipping');
    const summaryTax = $('#summary-tax');
    const summaryTotal = $('#summary-total');

    if (summarySubtotal) summarySubtotal.textContent = formatCurrency(subtotal);
    if (summaryTax) summaryTax.textContent = formatCurrency(tax);
    if (summaryTotal) summaryTotal.textContent = formatCurrency(total);
    
    if (discountRow && summaryDiscount) {
      if (discount > 0) {
        summaryDiscount.textContent = `-${formatCurrency(discount)}`;
        discountRow.hidden = false;
      } else {
        discountRow.hidden = true;
      }
    }

    if (summaryShipping) {
      if (State.step === 1) {
        summaryShipping.textContent = 'Calculated at next step';
        summaryShipping.classList.add('text-muted');
      } else {
        summaryShipping.textContent = shipping === 0 ? 'FREE' : formatCurrency(shipping);
        summaryShipping.classList.remove('text-muted');
      }
    }

    // All other summary locations
    $$('.subtotal-value').forEach(el => el.textContent = formatCurrency(subtotal));
    $$('.tax-value').forEach(el => el.textContent = formatCurrency(tax));
    $$('.total-value').forEach(el => el.textContent = formatCurrency(total));
    $$('.shipping-value').forEach(el => {
      el.textContent = shipping === 0 ? 'FREE' : formatCurrency(shipping);
    });
    
    $$('.discount-row').forEach(row => {
      if (discount > 0) {
        row.hidden = false;
        const val = row.querySelector('.discount-value');
        if (val) val.textContent = `-${formatCurrency(discount)}`;
      } else {
        row.hidden = true;
      }
    });

    // Mobile total
    const mobileTotal = $('#mobile-total');
    if (mobileTotal) mobileTotal.textContent = formatCurrency(total);
  }

  // ==========================================================================
  // CONFIG LOADING
  // ==========================================================================

  async function loadConfig() {
    const [taxRes, shipRes] = await Promise.all([
      api('/api/checkout/taxes/'),
      api('/api/checkout/shipping-zones/')
    ]);

    if (taxRes.ok && taxRes.data?.success) {
      State.config.taxRates = taxRes.data.provinces;
    }

    if (shipRes.ok && shipRes.data?.success) {
      State.config.shippingZones = shipRes.data.shipping_zones;
    }
  }

  async function loadAddresses() {
    const res = await api('/api/accounts/addresses/');
    if (res.ok && Array.isArray(res.data)) {
      State.addresses = res.data;
      renderSavedAddresses();
    }
  }

  function renderSavedAddresses() {
    const container = $('#saved-addresses');
    const list = $('#addresses-list');
    
    if (!container || !list || State.addresses.length === 0) return;

    container.hidden = false;

    list.innerHTML = State.addresses.map((addr, i) => `
      <div class="saved-address ${i === 0 ? 'saved-address--selected' : ''}" data-id="${addr.id}">
        <input type="radio" name="saved_address" value="${addr.id}" ${i === 0 ? 'checked' : ''}>
        <span class="saved-address__radio"></span>
        <div class="saved-address__content">
          <strong>${addr.first_name} ${addr.last_name}</strong><br>
          ${addr.address1}${addr.address2 ? ', ' + addr.address2 : ''}<br>
          ${addr.city}, ${addr.province} ${addr.postal_code}
        </div>
      </div>
    `).join('');

    if (State.addresses.length > 0) {
      fillShippingAddress(State.addresses[0]);
    }

    $$('.saved-address', list).forEach(el => {
      el.addEventListener('click', function() {
        const id = parseInt(this.dataset.id);
        const addr = State.addresses.find(a => a.id === id);
        if (addr) {
          fillShippingAddress(addr);
          $$('.saved-address', list).forEach(a => a.classList.remove('saved-address--selected'));
          this.classList.add('saved-address--selected');
          this.querySelector('input').checked = true;
        }
      });
    });
  }

  function fillShippingAddress(addr) {
    setVal('ship_first_name', addr.first_name);
    setVal('ship_last_name', addr.last_name);
    setVal('ship_company', addr.company);
    setVal('ship_email', addr.email);
    setVal('ship_phone', addr.phone);
    setVal('ship_address1', addr.address1);
    setVal('ship_address2', addr.address2);
    setVal('ship_city', addr.city);
    setVal('ship_province', addr.province);
    setVal('ship_postal', addr.postal_code);
    calculateTotals();
  }

  // ==========================================================================
  // SHIPPING OPTIONS
  // ==========================================================================

  function getBestShippingOptions(zones) {
    // Group by service type and get best (cheapest) option for each
    const typeMap = new Map();
    
    zones.forEach(zone => {
      const type = zone.method || 'standard';
      const existing = typeMap.get(type);
      
      // Keep the cheapest option for each type
      if (!existing || zone.base_cost < existing.base_cost) {
        typeMap.set(type, zone);
      }
    });
    
    // Sort by cost (free first, then cheapest to most expensive)
    return Array.from(typeMap.values()).sort((a, b) => a.base_cost - b.base_cost);
  }

  function renderShippingOptions() {
    const container = $('#shipping-options');
    if (!container) return;

    const allZones = State.config.shippingZones;
    
    if (allZones.length === 0) {
      container.innerHTML = `
        <div class="info-box">
          <span class="material-symbols-rounded">info</span>
          <p>No shipping options available for your location.</p>
        </div>
      `;
      return;
    }

    // Get only the best option for each service type
    const zones = getBestShippingOptions(allZones);

    container.innerHTML = zones.map((zone, i) => `
      <label class="shipping-option ${i === 0 ? 'shipping-option--selected' : ''}">
        <input type="radio" name="shipping_method" value="${zone.method}" ${i === 0 ? 'checked' : ''}>
        <span class="shipping-option__radio"></span>
        <span class="material-symbols-rounded shipping-option__icon">
          ${zone.method === 'express' ? 'bolt' : zone.method === 'overnight' ? 'flight' : 'local_shipping'}
        </span>
        <div class="shipping-option__details">
          <div class="shipping-option__name">${zone.label}</div>
          <div class="shipping-option__time">${zone.estimated_days || '3-5 business days'}</div>
        </div>
        <span class="shipping-option__price ${zone.base_cost === 0 ? 'shipping-option__price--free' : ''}">
          ${zone.base_cost === 0 ? 'FREE' : formatCurrency(zone.base_cost)}
        </span>
      </label>
    `).join('');

    // Select first by default
    if (zones.length > 0) {
      State.shipping = {
        method: zones[0].method,
        cost: zones[0].base_cost,
        label: zones[0].label,
        days: zones[0].estimated_days || '3-5 business days'
      };
    }

    // Attach event listeners
    $$('.shipping-option', container).forEach(el => {
      el.addEventListener('click', function() {
        const radio = this.querySelector('input');
        const zone = zones.find(z => z.method === radio.value);
        
        if (zone) {
          State.shipping = {
            method: zone.method,
            cost: zone.base_cost,
            label: zone.label,
            days: zone.estimated_days || '3-5 business days'
          };
          
          $$('.shipping-option', container).forEach(o => o.classList.remove('shipping-option--selected'));
          this.classList.add('shipping-option--selected');
          calculateTotals();
        }
      });
    });
  }

  // ==========================================================================
  // NAVIGATION
  // ==========================================================================

  function goToStep(step) {
    if (step < 1 || step > State.maxSteps) return;
    
    // Validate current step before advancing
    if (step > State.step && !validateStep(State.step)) return;

    // Hide all steps
    $$('.step').forEach(el => {
      el.classList.remove('step--active');
      el.hidden = true;
    });

    // Show target step
    const target = $(`.step[data-step="${step}"]`);
    if (target) {
      target.classList.add('step--active');
      target.hidden = false;
    }

    // Update progress
    updateProgress(step);
    State.step = step;

    // Step-specific actions
    if (step === 2) {
      renderShippingOptions();
      renderSidebarItems();
    } else if (step === 3) {
      renderSidebarItems();
    } else if (step === 4) {
      populateReviewPage();
      renderSidebarItems();
    }

    calculateTotals();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function updateProgress(step) {
    const fill = $('.progress__fill');
    const steps = $$('.progress__step');
    const visibleSteps = 4; // Cart, Shipping, Payment, Review (Confirmed is separate)

    steps.forEach((el, i) => {
      const num = i + 1;
      el.classList.remove('progress__step--active', 'progress__step--completed');
      el.removeAttribute('aria-current');

      if (num < step) {
        el.classList.add('progress__step--completed');
      } else if (num === step) {
        el.classList.add('progress__step--active');
        el.setAttribute('aria-current', 'step');
      }
    });

    if (fill) {
      // Progress based on 4 visible steps, full at step 4 (Review)
      const pct = Math.min(((step - 1) / (visibleSteps - 1)) * 100, 100);
      fill.style.width = `${pct}%`;
    }
  }

  // ==========================================================================
  // REVIEW PAGE
  // ==========================================================================

  function populateReviewPage() {
    // Products
    const reviewCart = $('#review-cart');
    if (reviewCart) {
      reviewCart.innerHTML = State.cart.map(item => `
        <div class="review-item">
          <div class="review-item__image">
            ${item.image 
              ? `<img src="${item.image}" alt="${item.productName}">` 
              : '<span class="material-symbols-rounded" style="font-size:1.5rem;color:#ccc;">inventory_2</span>'
            }
          </div>
          <div class="review-item__details">
            <div class="review-item__name">${item.productName}</div>
            <div class="review-item__meta">
              ${item.variant ? `${item.variant} · ` : ''}Qty: ${item.quantity}
            </div>
          </div>
          <div class="review-item__price">${formatCurrency(item.price * item.quantity)}</div>
        </div>
      `).join('');
    }

    // Shipping Address
    const reviewShipping = $('#review-shipping-address');
    if (reviewShipping) {
      reviewShipping.innerHTML = `
        <strong>${getVal('ship_first_name')} ${getVal('ship_last_name')}</strong>
        ${getVal('ship_company') ? `<br>${getVal('ship_company')}` : ''}
        <br>${getVal('ship_address1')}
        ${getVal('ship_address2') ? `<br>${getVal('ship_address2')}` : ''}
        <br>${getVal('ship_city')}, ${getVal('ship_province')} ${getVal('ship_postal')}
        <br>Canada
        <br>${getVal('ship_phone')}
      `;
    }

    // Billing Address
    const billingSection = $('#review-billing-section');
    const reviewBilling = $('#review-billing-address');
    const billingSame = $('input[name="billing_same"]:checked')?.value === 'same';

    if (billingSection && reviewBilling) {
      if (billingSame) {
        billingSection.hidden = true;
      } else {
        billingSection.hidden = false;
        reviewBilling.innerHTML = `
          <strong>${getVal('bill_first_name')} ${getVal('bill_last_name')}</strong>
          <br>${getVal('bill_address1')}
          ${getVal('bill_address2') ? `<br>${getVal('bill_address2')}` : ''}
          <br>${getVal('bill_city')}, ${getVal('bill_province')} ${getVal('bill_postal')}
          <br>Canada
        `;
      }
    }

    // Payment
    const reviewPayment = $('#review-payment');
    const paymentMethod = $('input[name="payment_method"]:checked')?.value;
    
    if (reviewPayment) {
      if (paymentMethod === 'card') {
        const cardNum = getVal('card_number').replace(/\s/g, '');
        const lastFour = cardNum.slice(-4);
        reviewPayment.innerHTML = `
          <span class="material-symbols-rounded">credit_card</span>
          <div class="review-payment__details">
            <div class="review-payment__method">Credit/Debit Card</div>
            <div class="review-payment__card">•••• •••• •••• ${lastFour || '****'}</div>
          </div>
        `;
      } else {
        reviewPayment.innerHTML = `
          <span class="material-symbols-rounded">account_balance</span>
          <div class="review-payment__details">
            <div class="review-payment__method">Bank Transfer</div>
            <div class="review-payment__card">Payment instructions will be sent via email</div>
          </div>
        `;
      }
    }
  }

  // ==========================================================================
  // CONFIRMATION PAGE
  // ==========================================================================

  function populateConfirmation(order) {
    const now = new Date();

    // Header
    $('#conf-order-number').textContent = order.order_number || 'PKX' + Date.now();
    $('#conf-date').textContent = formatDate(now);
    $('#conf-time').textContent = formatTime(now);
    $('#conf-status').textContent = order.status || 'Pending';
    $('#conf-placed-date').textContent = formatShortDate(now);

    // Items
    const confItems = $('#conf-items');
    const itemCount = $('#conf-item-count');
    
    if (confItems) {
      confItems.innerHTML = State.cart.map(item => `
        <div class="conf-item">
          <div class="conf-item__image">
            ${item.image 
              ? `<img src="${item.image}" alt="${item.productName}">` 
              : '<span class="material-symbols-rounded" style="font-size:1.5rem;color:#ccc;">inventory_2</span>'
            }
          </div>
          <div class="conf-item__details">
            <div class="conf-item__name">${item.productName}</div>
            <div class="conf-item__meta">
              ${item.sku ? `SKU: ${item.sku}` : ''}
              ${item.variant ? ` · ${item.variant}` : ''}
              <br>Qty ${item.quantity}
            </div>
          </div>
          <div class="conf-item__price">
            <div class="conf-item__price-total">${formatCurrency(item.price * item.quantity)}</div>
            <div class="conf-item__price-unit">${formatCurrency(item.price)} each</div>
          </div>
        </div>
      `).join('');
    }

    if (itemCount) {
      const total = State.cart.reduce((sum, i) => sum + i.quantity, 0);
      itemCount.textContent = `${total} item${total !== 1 ? 's' : ''}`;
    }

    // Totals
    $('#conf-subtotal').textContent = formatCurrency(State.totals.subtotal);
    $('#conf-shipping-cost').textContent = State.totals.shipping === 0 ? 'FREE' : formatCurrency(State.totals.shipping);
    $('#conf-tax').textContent = formatCurrency(State.totals.tax);
    $('#conf-total').textContent = formatCurrency(State.totals.total);

    if (State.totals.discount > 0) {
      $('#conf-discount-row').hidden = false;
      $('#conf-discount').textContent = `-${formatCurrency(State.totals.discount)}`;
    }

    // Payment method
    const paymentMethod = $('input[name="payment_method"]:checked')?.value;
    $('#conf-payment-method').textContent = paymentMethod === 'card' ? 'Credit Card' : 'Bank Transfer';

    // Shipping Address
    const confShipAddress = $('#conf-ship-address');
    if (confShipAddress) {
      confShipAddress.innerHTML = `
        ${getVal('ship_first_name')} ${getVal('ship_last_name')}<br>
        ${getVal('ship_address1')}<br>
        ${getVal('ship_address2') ? getVal('ship_address2') + '<br>' : ''}
        ${getVal('ship_city')}, ${getVal('ship_province')} ${getVal('ship_postal')}<br>
        CA<br>
        ${getVal('ship_phone')}
      `;
    }

    // Billing Address
    const confBillSection = $('#conf-bill-section');
    const confBillAddress = $('#conf-bill-address');
    const billingSame = $('input[name="billing_same"]:checked')?.value === 'same';

    if (confBillSection && confBillAddress) {
      if (billingSame) {
        confBillAddress.innerHTML = confShipAddress.innerHTML;
      } else {
        confBillAddress.innerHTML = `
          ${getVal('bill_first_name')} ${getVal('bill_last_name')}<br>
          ${getVal('bill_address1')}<br>
          ${getVal('bill_address2') ? getVal('bill_address2') + '<br>' : ''}
          ${getVal('bill_city')}, ${getVal('bill_province')} ${getVal('bill_postal')}<br>
          CA
        `;
      }
    }
  }

  // ==========================================================================
  // VALIDATION
  // ==========================================================================

  const validators = {
    email: v => !v ? 'Email is required' : !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) ? 'Invalid email address' : null,
    phone: v => !v ? 'Phone is required' : v.replace(/\D/g, '').length < 10 ? 'Invalid phone number' : null,
    required: v => !v?.trim() ? 'This field is required' : null,
    postal: v => !v ? 'Postal code is required' : !/^[A-Z]\d[A-Z]\s?\d[A-Z]\d$/i.test(v) ? 'Invalid postal code (e.g., M5V 3A8)' : null,
    card: v => !v ? 'Card number is required' : v.replace(/\s/g, '').length < 13 ? 'Invalid card number' : null,
    expiry: v => {
      if (!v) return 'Expiry is required';
      const m = v.match(/^(\d{2})\/(\d{2})$/);
      if (!m) return 'Use MM/YY format';
      const [, month, year] = m;
      if (parseInt(month) < 1 || parseInt(month) > 12) return 'Invalid month';
      const now = new Date();
      const exp = new Date(2000 + parseInt(year), parseInt(month) - 1);
      return exp < now ? 'Card is expired' : null;
    },
    cvc: v => !v ? 'CVC is required' : !/^\d{3,4}$/.test(v) ? 'Invalid CVC' : null
  };

  function validateField(input) {
    const name = input.name || input.id;
    const value = input.value.trim();
    let error = null;

    // Skip validation for hidden fields
    if (input.closest('[hidden]')) return true;

    switch (name) {
      case 'ship_email':
        error = validators.email(value);
        break;
      case 'ship_phone':
        error = validators.phone(value);
        break;
      case 'ship_postal':
      case 'bill_postal':
        error = validators.postal(value);
        break;
      case 'card_number':
        error = validators.card(value);
        break;
      case 'card_expiry':
        error = validators.expiry(value);
        break;
      case 'card_cvc':
        error = validators.cvc(value);
        break;
      default:
        if (input.required) {
          error = validators.required(value);
        }
    }

    const group = input.closest('.form-group');
    
    if (error) {
      input.classList.add('error');
      input.classList.add('success');
    } else {
      input.classList.remove('error');
      input.classList.remove('success');
    }

    return !error;
  }

  function validateStep(step) {
    const stepEl = $(`.step[data-step="${step}"]`);
    if (!stepEl) return true;

    let isValid = true;
    let errorMessages = [];

    // Step 1: Cart - just need items
    if (step === 1) {
      if (State.cart.length === 0) {
        showToast('warning', 'Empty Cart', 'Please add items to your cart before continuing.');
        return false;
      }
      return true;
    }

    // Step 2: Shipping
    if (step === 2) {
      const shippingFields = ['ship_first_name', 'ship_last_name', 'ship_email', 'ship_phone', 
                              'ship_address1', 'ship_city', 'ship_province', 'ship_postal'];
      
      shippingFields.forEach(id => {
        const input = document.getElementById(id);
        if (input && !validateField(input)) {
          isValid = false;
        }
      });

      if (!State.shipping.method) {
        showToast('warning', 'Shipping Required', 'Please select a shipping method.');
        return false;
      }

      if (!isValid) {
        showToast('error', 'Missing Information', 'Please fill in all required shipping fields.');
      }
    }

    // Step 3: Payment
    if (step === 3) {
      const paymentMethod = $('input[name="payment_method"]:checked')?.value;
      
      if (paymentMethod === 'card') {
        const cardFields = ['card_number', 'card_expiry', 'card_cvc', 'card_name'];
        cardFields.forEach(id => {
          const input = document.getElementById(id);
          if (input && !validateField(input)) {
            isValid = false;
          }
        });
        
        if (!isValid) {
          showToast('error', 'Invalid Card Details', 'Please check your payment information.');
        }
      }

      const billingSame = $('input[name="billing_same"]:checked')?.value === 'same';
      if (!billingSame) {
        const billingFields = ['bill_first_name', 'bill_last_name', 'bill_address1', 
                               'bill_city', 'bill_province', 'bill_postal'];
        billingFields.forEach(id => {
          const input = document.getElementById(id);
          if (input && !validateField(input)) {
            isValid = false;
          }
        });
        
        if (!isValid) {
          showToast('error', 'Missing Information', 'Please fill in all required billing fields.');
        }
      }
    }

    // Step 4: Review
    if (step === 4) {
      const terms = $('#terms');
      if (terms && !terms.checked) {
        terms.closest('.checkbox')?.querySelector('.checkbox__box')?.classList.add('error');
        showToast('warning', 'Terms Required', 'Please agree to the Terms and Conditions to continue.');
        return false;
      }
    }

    if (!isValid) {
      const firstError = stepEl.querySelector('.error');
      if (firstError) {
        firstError.focus();
        firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }

    return isValid;
  }

  // ==========================================================================
  // PAYMENT FORMATTING
  // ==========================================================================

  function formatCardNumber(value) {
    const v = value.replace(/\D/g, '');
    const parts = v.match(/.{1,4}/g);
    return parts ? parts.join(' ').substring(0, 19) : '';
  }

  function formatExpiry(value) {
    const v = value.replace(/\D/g, '');
    if (v.length >= 2) {
      return v.substring(0, 2) + '/' + v.substring(2, 4);
    }
    return v;
  }

  function detectCardBrand(num) {
    const v = num.replace(/\D/g, '');
    if (/^4/.test(v)) return 'visa';
    if (/^5[1-5]|^2[2-7]/.test(v)) return 'mastercard';
    if (/^3[47]/.test(v)) return 'amex';
    return null;
  }

  function updateCardBrandIcon(brand) {
    const container = $('#card-brand');
    if (!container) return;
    
    if (brand) {
      container.innerHTML = `<img src="/static/images/cards/${brand}.svg" alt="${brand}" height="24">`;
    } else {
      container.innerHTML = '';
    }
  }

  // ==========================================================================
  // PROMO CODE
  // ==========================================================================

  async function applyPromoCode(input, messageEl, btn) {
    const code = input?.value?.trim();
    if (!code) {
      showToast('warning', 'Enter Code', 'Please enter a promo code.');
      return;
    }

    if (btn) setButtonLoading(btn, true);

    const res = await api('/api/coupons/validate/', {
      method: 'POST',
      body: JSON.stringify({ code, subtotal: State.totals.subtotal })
    });

    if (btn) setButtonLoading(btn, false);

    if (res.ok && res.data?.valid) {
      State.coupon = {
        code: res.data.code,
        discount: res.data.discount_value,
        type: res.data.discount_type
      };

      const discountText = State.coupon.type === 'percentage' 
        ? `${State.coupon.discount}% off` 
        : `${formatCurrency(State.coupon.discount)} off`;

      if (messageEl) {
        messageEl.textContent = `✓ Applied: ${discountText}`;
        messageEl.className = 'promo__message promo__message--success';
        messageEl.hidden = false;
      }

      showToast('success', 'Promo Applied', `You saved ${discountText} on your order!`);

      input.disabled = true;
      input.classList.add('success');
      calculateTotals();
    } else {
      if (messageEl) {
        messageEl.textContent = res.data?.message || 'Invalid promo code';
        messageEl.className = 'promo__message promo__message--error';
        messageEl.hidden = false;
      }
      showToast('error', 'Invalid Code', res.data?.message || 'This promo code is invalid or expired.');
    }
  }

  // ==========================================================================
  // ORDER SUBMISSION
  // ==========================================================================

  async function placeOrder() {
    if (State.processing) return;
    if (!validateStep(4)) return;

    State.processing = true;
    const overlay = $('#processing-overlay');
    const btn = $('#place-order-btn');

    if (overlay) overlay.hidden = false;
    if (btn) setButtonLoading(btn, true);

    try {
      const billingSame = $('input[name="billing_same"]:checked')?.value === 'same';
      const paymentMethod = $('input[name="payment_method"]:checked')?.value;

      // Format data to match API expected structure
      const orderData = {
        items: State.cart.map(item => ({
          product_id: item.productId,
          variant_id: item.variantId || null,
          quantity: item.quantity,
          price: item.price
        })),
        address: {
          first_name: getVal('ship_first_name'),
          last_name: getVal('ship_last_name'),
          company: getVal('ship_company'),
          email: getVal('ship_email'),
          phone: getVal('ship_phone'),
          street_address: getVal('ship_address1'),
          street_address_2: getVal('ship_address2'),
          city: getVal('ship_city'),
          province: getVal('ship_province'),
          postal_code: getVal('ship_postal'),
          country: 'Canada'
        },
        billing_address: billingSame ? null : {
          first_name: getVal('bill_first_name'),
          last_name: getVal('bill_last_name'),
          street_address: getVal('bill_address1'),
          street_address_2: getVal('bill_address2'),
          city: getVal('bill_city'),
          province: getVal('bill_province'),
          postal_code: getVal('bill_postal'),
          country: 'Canada'
        },
        guest_email: getVal('ship_email'),
        shipping: {
          method: State.shipping.method,
          cost: State.shipping.cost,
          label: State.shipping.label
        },
        payment_method: paymentMethod,
        coupon: State.coupon ? { code: State.coupon.code } : null,
        newsletter: $('#newsletter')?.checked || false,
        totals: {
          subtotal: State.totals.subtotal,
          tax: State.totals.tax,
          shipping: State.totals.shipping,
          discount: State.totals.discount,
          total: State.totals.total
        }
      };

      const res = await api('/api/order/create/', {
        method: 'POST',
        body: JSON.stringify(orderData)
      });

      if (res.ok && res.data?.success) {
        State.order = res.data;
        
        // Populate and show confirmation
        populateConfirmation(res.data);
        
        // Clear cart
        localStorage.removeItem('packaxis_cart');
        window.dispatchEvent(new CustomEvent('cart:updated', { detail: { count: 0 } }));
        
        // Go to confirmation step
        goToStep(5);
        
        showToast('success', 'Order Placed!', 'Thank you for your order. You will receive a confirmation email shortly.');
      } else {
        throw new Error(res.data?.message || 'Failed to create order');
      }
    } catch (e) {
      console.error('Order error:', e);
      showToast('error', 'Order Failed', e.message || 'Something went wrong. Please try again.');
    } finally {
      State.processing = false;
      if (overlay) overlay.hidden = true;
      if (btn) setButtonLoading(btn, false);
    }
  }

  // ==========================================================================
  // EVENT LISTENERS
  // ==========================================================================

  function setupEventListeners() {
    // Navigation buttons
    $$('[data-next]').forEach(btn => {
      btn.addEventListener('click', () => goToStep(parseInt(btn.dataset.next)));
    });

    $$('[data-prev]').forEach(btn => {
      btn.addEventListener('click', () => goToStep(parseInt(btn.dataset.prev)));
    });

    $$('[data-goto]').forEach(btn => {
      btn.addEventListener('click', () => goToStep(parseInt(btn.dataset.goto)));
    });

    // Progress step clicks (only go back)
    $$('.progress__step').forEach(step => {
      step.addEventListener('click', () => {
        const num = parseInt(step.dataset.step);
        if (num < State.step) goToStep(num);
      });
    });

    // Field validation on blur
    $$('.form-input, .form-select').forEach(input => {
      input.addEventListener('blur', () => validateField(input));
    });

    // Province change recalculates tax
    $('#ship_province')?.addEventListener('change', calculateTotals);

    // Card number formatting
    const cardNumber = $('#card_number');
    if (cardNumber) {
      cardNumber.addEventListener('input', (e) => {
        e.target.value = formatCardNumber(e.target.value);
        updateCardBrandIcon(detectCardBrand(e.target.value));
      });
    }

    // Expiry formatting
    const cardExpiry = $('#card_expiry');
    if (cardExpiry) {
      cardExpiry.addEventListener('input', (e) => {
        e.target.value = formatExpiry(e.target.value);
      });
    }

    // CVC
    const cardCvc = $('#card_cvc');
    if (cardCvc) {
      cardCvc.addEventListener('input', (e) => {
        e.target.value = e.target.value.replace(/\D/g, '').substring(0, 4);
      });
    }

    // Phone formatting
    const phone = $('#ship_phone');
    if (phone) {
      phone.addEventListener('input', (e) => {
        let v = e.target.value.replace(/\D/g, '');
        if (v.length >= 10) {
          v = `(${v.substring(0,3)}) ${v.substring(3,6)}-${v.substring(6,10)}`;
        }
        e.target.value = v;
      });
    }

    // Postal code formatting
    const postal = $('#ship_postal');
    if (postal) {
      postal.addEventListener('input', (e) => {
        let v = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
        if (v.length > 3) {
          v = v.substring(0, 3) + ' ' + v.substring(3, 6);
        }
        e.target.value = v;
      });
    }

    // Payment method toggle
    $$('input[name="payment_method"]').forEach(radio => {
      radio.addEventListener('change', () => {
        const cardForm = $('#card-form');
        const bankForm = $('#bank-form');
        
        $$('.payment-method').forEach(m => m.classList.remove('payment-method--selected'));
        radio.closest('.payment-method')?.classList.add('payment-method--selected');
        
        if (radio.value === 'card') {
          if (cardForm) cardForm.hidden = false;
          if (bankForm) bankForm.hidden = true;
        } else {
          if (cardForm) cardForm.hidden = true;
          if (bankForm) bankForm.hidden = false;
        }
      });
    });

    // Billing address toggle
    $$('input[name="billing_same"]').forEach(radio => {
      radio.addEventListener('change', () => {
        const billingForm = $('#billing-form');
        
        $$('.billing-option').forEach(o => o.classList.remove('billing-option--selected'));
        radio.closest('.billing-option')?.classList.add('billing-option--selected');
        
        if (billingForm) {
          billingForm.hidden = radio.value === 'same';
        }
      });
    });

    // New address button
    $('#new-address-btn')?.addEventListener('click', () => {
      $$('.saved-address').forEach(el => {
        el.classList.remove('saved-address--selected');
        const input = el.querySelector('input');
        if (input) input.checked = false;
      });
      
      // Clear form
      ['ship_first_name', 'ship_last_name', 'ship_company', 'ship_email', 'ship_phone',
       'ship_address1', 'ship_address2', 'ship_city', 'ship_province', 'ship_postal'
      ].forEach(id => setVal(id, ''));
    });

    // Promo code - Step 1
    const promoInput = $('#promo-code');
    const promoMessage = $('#promo-message');
    const applyPromoBtn = $('#apply-promo');
    
    if (applyPromoBtn && promoInput) {
      applyPromoBtn.addEventListener('click', () => applyPromoCode(promoInput, promoMessage, applyPromoBtn));
      promoInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          applyPromoCode(promoInput, promoMessage, applyPromoBtn);
        }
      });
    }

    // Promo code - Other steps (sync with main promo)
    $$('.apply-promo-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const input = btn.closest('.promo').querySelector('.promo-input');
        const msg = btn.closest('.promo').querySelector('.promo-msg');
        applyPromoCode(input, msg, btn);
      });
    });

    // Form submit
    $('#checkout-form')?.addEventListener('submit', (e) => {
      e.preventDefault();
      placeOrder();
    });

    // Mobile summary toggle
    const summaryToggle = $('#mobile-summary-toggle');
    if (summaryToggle) {
      summaryToggle.addEventListener('click', function() {
        const expanded = this.getAttribute('aria-expanded') === 'true';
        this.setAttribute('aria-expanded', !expanded);
        
        // Toggle sidebar visibility on mobile
        const sidebar = $('.checkout__sidebar');
        if (sidebar) {
          sidebar.classList.toggle('checkout__sidebar--mobile-open', !expanded);
        }
      });
    }

    // Terms checkbox
    $('#terms')?.addEventListener('change', function() {
      this.closest('.checkbox')?.querySelector('.checkbox__box')?.classList.remove('error');
    });
  }

  // ==========================================================================
  // INITIALIZATION
  // ==========================================================================

  async function init() {
    loadCart();
    renderCart();
    renderSidebarItems();
    
    await loadConfig();
    await loadAddresses();
    
    calculateTotals();
    updateProgress(1);
    setupEventListeners();
  }

  // Start
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
