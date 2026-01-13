type CartItem = {
  productId: number;
  productName: string;
  price: number;
  retailPrice: number; // Store original retail price
  pricingTiers?: PricingTier[]; // Store pricing tiers for bulk calculation
  image?: string;
  quantity: number;
};

type PricingTier = {
  minQty: number;
  maxQty: number;
  price: number;
};

const STORAGE_KEY = 'packaxis_cart';

function readItems(): CartItem[] {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return [];
  try { return JSON.parse(raw) as CartItem[]; } catch { return []; }
}

function writeItems(items: CartItem[]): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
}

// Calculate applicable price based on quantity and pricing tiers
function getApplicablePrice(item: CartItem): number {
  if (!item.pricingTiers || item.pricingTiers.length === 0) {
    return item.retailPrice || item.price;
  }
  
  // Check if quantity falls into any bulk pricing tier
  for (const tier of item.pricingTiers) {
    if (item.quantity >= tier.minQty && (tier.maxQty >= item.quantity || tier.maxQty >= 9999)) {
      return tier.price;
    }
  }
  
  // Return retail price if no tier matches
  return item.retailPrice || item.price;
}

function totals(items: CartItem[]) {
  const subtotal = items.reduce((sum, item) => {
    const applicablePrice = getApplicablePrice(item);
    return sum + applicablePrice * item.quantity;
  }, 0);
  const tax = subtotal * 0.13;
  const total = subtotal + tax;
  const itemCount = items.reduce((sum, item) => sum + item.quantity, 0);
  return { subtotal, tax, total, itemCount };
}

function updateBadge(count: number) {
  const badge = document.getElementById('cart-badge');
  if (badge) {
    badge.textContent = String(count);
    badge.classList.toggle('is-hidden', count === 0);
  }
}

function renderCartDropdown(items: CartItem[]) {
  const container = document.querySelector('.cart-dropdown');
  if (!container) return;

  if (!items.length) {
    container.innerHTML = `
      <div class="cart-dropdown-empty">
        <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
          <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/>
          <line x1="3" y1="6" x2="21" y2="6"/>
          <path d="M16 10a4 4 0 0 1-8 0"/>
        </svg>
        <p class="cart-dropdown-empty-title">Your cart is empty</p>
        <p class="cart-dropdown-empty-subtitle">Start shopping to add items</p>
        <a href="/products/" class="cart-dropdown-shop-btn">Continue Shopping</a>
      </div>
    `;
  } else {
    const { itemCount, subtotal } = totals(items);
    const displayCount = Math.min(items.length, 3);
    const moreCount = items.length - displayCount;
    
    const itemsHtml = items.slice(0, 3).map(item => {
      const applicablePrice = getApplicablePrice(item);
      const itemTotal = applicablePrice * item.quantity;
      const isBulkPrice = item.pricingTiers && item.pricingTiers.length > 0 && applicablePrice < (item.retailPrice || item.price);
      
      return `
      <div class="cart-dropdown-item" data-product-id="${item.productId}">
        <div class="cart-dropdown-item-image">
          ${item.image ? `<img src="${item.image}" alt="${item.productName}">` : `<div class="cart-dropdown-placeholder">📦</div>`}
        </div>
        <div class="cart-dropdown-item-details">
          <div class="cart-dropdown-item-name">${item.productName}</div>
          <div class="cart-dropdown-item-meta">
            <span class="cart-dropdown-item-qty">Qty: ${item.quantity}</span>
            <span class="cart-dropdown-item-price ${isBulkPrice ? 'bulk-price' : ''}">
              $${itemTotal.toFixed(2)}
              ${isBulkPrice ? '<span class="bulk-badge">Bulk</span>' : ''}
            </span>
          </div>
          ${isBulkPrice ? `<div class="cart-dropdown-item-unit-price">$${applicablePrice.toFixed(2)}/unit</div>` : ''}
        </div>
        <button class="cart-dropdown-item-remove" data-product-id="${item.productId}" aria-label="Remove item">×</button>
      </div>
    `;
    }).join('');

    container.innerHTML = `
      <div class="cart-dropdown-header">
        <h4 class="cart-dropdown-header-title">🛒 Shopping Cart</h4>
        <span class="cart-dropdown-badge">${itemCount}</span>
      </div>
      <div class="cart-dropdown-items">
        ${itemsHtml}
        ${moreCount > 0 ? `<div class="cart-dropdown-more-items">+ ${moreCount} more item${moreCount > 1 ? 's' : ''}</div>` : ''}
      </div>
      <div class="cart-dropdown-divider"></div>
      <div class="cart-dropdown-footer">
        <div class="cart-dropdown-subtotal">
          <span class="cart-dropdown-subtotal-label">Subtotal:</span>
          <span class="cart-dropdown-subtotal-value">$${subtotal.toFixed(2)}</span>
        </div>
        <a href="/cart/" class="cart-dropdown-view-btn">View Cart</a>
        <a href="/checkout/" class="cart-dropdown-checkout-btn">Proceed to Checkout</a>
      </div>
    `;
    
    // Bind remove buttons
    container.querySelectorAll('.cart-dropdown-item-remove').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const id = Number((btn as HTMLElement).dataset.productId);
        removeItem(id);
      });
    });
  }
}

function renderCartPage(items: CartItem[]) {
  const container = document.getElementById('cart-items-container');
  if (!container) return;
  const { subtotal, tax, total } = totals(items);

  if (!items.length) {
    container.innerHTML = `
      <div class="cart-card">
        <div class="cart-empty">
          <div class="cart-empty__icon" aria-hidden="true">🛒</div>
          <h3 class="cart-empty__title">Your cart is empty</h3>
          <p class="cart-empty__subtitle">Add some eco-friendly paper bags to get started!</p>
          <a href="/products/" class="btn btn-primary">Shop Products</a>
        </div>
      </div>
    `;
  } else {
    const placeholderSvg = 'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22120%22 height=%22120%22 viewBox=%220 0 120 120%22%3E%3Crect fill=%22%23f0f0f0%22 width=%22120%22 height=%22120%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 dy=%22.3em%22 fill=%22%23999%22 font-family=%22Arial%22 font-size=%2214%22%3ENo Image%3C/text%3E%3C/svg%3E';
    const html = items.map(item => {
      const applicablePrice = getApplicablePrice(item);
      const itemTotal = applicablePrice * item.quantity;
      const isBulkPrice = item.pricingTiers && item.pricingTiers.length > 0 && applicablePrice < (item.retailPrice || item.price);
      
      return `
      <div class="cart-item">
        <img src="${item.image || placeholderSvg}" alt="${item.productName}" class="cart-item__image">
        <div class="cart-item__details">
          <h3 class="cart-item__title">${item.productName}</h3>
          <p class="cart-item__sku">Product ID: ${item.productId}</p>
          <div class="cart-qty">
            <button class="qty-btn" data-cart-dec="${item.productId}" aria-label="Decrease quantity">−</button>
            <input type="number" value="${item.quantity}" min="1" readonly class="qty-input" aria-label="Quantity">
            <button class="qty-btn" data-cart-inc="${item.productId}" aria-label="Increase quantity">+</button>
          </div>
          <button class="cart-remove" data-cart-remove="${item.productId}">Remove</button>
        </div>
        <div class="cart-item__price">
          $${itemTotal.toFixed(2)}
          <div class="text-muted text-sm">
            $${applicablePrice.toFixed(2)} each
            ${isBulkPrice ? '<span class="bulk-price-badge">Bulk Price</span>' : ''}
          </div>
        </div>
      </div>
    `;
    }).join('');
    container.innerHTML = `<div class="cart-card">${html}</div>`;

    container.querySelectorAll('[data-cart-dec]').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = Number((btn as HTMLElement).dataset.cartDec);
        changeQuantity(id, -1);
      });
    });
    container.querySelectorAll('[data-cart-inc]').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = Number((btn as HTMLElement).dataset.cartInc);
        changeQuantity(id, 1);
      });
    });
    container.querySelectorAll('[data-cart-remove]').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = Number((btn as HTMLElement).dataset.cartRemove);
        removeItem(id);
      });
    });
  }

  const subtotalEl = document.getElementById('subtotal');
  const taxEl = document.getElementById('tax');
  const totalEl = document.getElementById('total');
  if (subtotalEl) subtotalEl.textContent = '$' + subtotal.toFixed(2);
  if (taxEl) taxEl.textContent = '$' + tax.toFixed(2);
  if (totalEl) totalEl.textContent = '$' + total.toFixed(2);
}

function syncUI() {
  const items = readItems();
  const { itemCount } = totals(items);
  updateBadge(itemCount);
  renderCartDropdown(items);
  if (window.location.pathname === '/checkout/') {
    renderCartPage(items);
  }
}

function addItem(productId: number, productName: string, price: number, image: string, quantity = 1, pricingTiers?: PricingTier[]) {
  const items = readItems();
  const existing = items.find(i => i.productId === productId);
  if (existing) {
    existing.quantity += quantity;
    // Update pricing tiers if provided
    if (pricingTiers) {
      existing.pricingTiers = pricingTiers;
      existing.retailPrice = price;
    }
  } else {
    items.push({ 
      productId, 
      productName, 
      price, 
      retailPrice: price,
      pricingTiers: pricingTiers || [],
      image, 
      quantity 
    });
  }
  writeItems(items);
  syncUI();
}

function removeItem(productId: number) {
  const items = readItems().filter(i => i.productId !== productId);
  writeItems(items);
  syncUI();
}

function changeQuantity(productId: number, delta: number) {
  const items = readItems();
  const target = items.find(i => i.productId === productId);
  if (!target) return;
  target.quantity = Math.max(1, target.quantity + delta);
  writeItems(items);
  syncUI();
}

function bindAddToCartButtons() {
  // Use event delegation on document to catch dynamically added buttons too
  document.addEventListener('click', (ev) => {
    const btn = (ev.target as HTMLElement).closest('[data-add-to-cart]');
    if (!btn) return;
    
    ev.preventDefault();
    const productId = Number((btn as HTMLElement).dataset.productId);
    const productName = (btn as HTMLElement).dataset.productName || 'Item';
    const price = Number((btn as HTMLElement).dataset.price || 0);
    const image = (btn as HTMLElement).dataset.image || '';
    const qtySelector = (btn as HTMLElement).dataset.qtySelector;
    const quantity = qtySelector ? Number((document.querySelector(qtySelector) as HTMLInputElement)?.value || 1) : 1;
    
    // Get pricing tiers from data attribute if available
    const pricingTiersData = (btn as HTMLElement).dataset.pricingTiers;
    let pricingTiers: PricingTier[] | undefined;
    if (pricingTiersData) {
      try {
        pricingTiers = JSON.parse(pricingTiersData);
      } catch (e) {
        console.warn('Failed to parse pricing tiers:', e);
      }
    }
    
    addItem(productId, productName, price, image, quantity, pricingTiers);
  });
}

export function initCart(): void {
  bindAddToCartButtons();
  syncUI();
}

// expose for legacy templates if needed
(window as any).Cart = { addItem, removeItem, changeQuantity, initCart };
