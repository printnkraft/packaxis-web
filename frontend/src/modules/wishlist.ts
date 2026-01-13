import { api, flags, analytics } from './shared';

type WishlistBtn = HTMLElement & { dataset: { productId?: string; inWishlist?: string } };

function setButtonState(btn: WishlistBtn, isIn: boolean) {
  btn.dataset.inWishlist = isIn ? '1' : '0';

  // Handle product card v2 wishlist buttons with material icons
  if (btn.classList.contains('product-card-v2__wishlist')) {
    const icon = btn.querySelector('.material-symbols-rounded');
    if (icon) {
      icon.textContent = isIn ? 'favorite' : 'favorite_border';
    }
    btn.classList.toggle('is-active', isIn);
    return;
  }

  // Handle PDP wishlist button
  if (btn.id === 'pdp-wishlist-btn') {
    const icon = btn.querySelector('.material-symbols-rounded');
    if (icon) {
      icon.textContent = isIn ? 'favorite' : 'favorite_border';
    }
    btn.classList.toggle('is-active', isIn);
    // Update button text
    const textNode = Array.from(btn.childNodes).find(node => node.nodeType === Node.TEXT_NODE);
    if (textNode) {
      textNode.textContent = isIn ? ' Saved' : ' Wishlist';
    }
    return;
  }

  if (isIn) {
    btn.classList.remove('btn-secondary');
    btn.classList.add('btn-primary');
    btn.innerHTML = '' + (btn.classList.contains('wishlist-toggle') ? ' Saved' : '');
  } else {
    btn.classList.remove('btn-primary');
    btn.classList.add('btn-secondary');
    btn.innerHTML = '' + (btn.classList.contains('wishlist-toggle') ? ' Wishlist' : '');
  }
}

async function loadState() {
  try {
    const res = await api.get('/api/wishlist/items/');
    if (!res.ok || !Array.isArray(res.body) && !res.body?.results && !res.body?.items) return;
    const list = Array.isArray(res.body) ? res.body : (res.body.results || res.body.items || []);
    const ids = new Set<number>((list.map((it: any) => it.product?.id).filter(Boolean)) as number[]);
    document.querySelectorAll<WishlistBtn>('.wishlist-btn, .wishlist-toggle, .product-card-v2__wishlist, #pdp-wishlist-btn').forEach(btn => {
      const pid = Number(btn.dataset.productId);
      if (ids.has(pid)) setButtonState(btn, true);
    });
  } catch {
    /* ignore */
  }
}

async function toggle(btn: WishlistBtn, productId: number) {
  const isIn = btn.dataset.inWishlist === '1';
  try {
    if (!isIn) {
      await api.post('/api/wishlist/items/', { product_id: productId });
      setButtonState(btn, true);
      analytics.track('wishlist:add', { productId });
    } else {
      const resp = await api.del(`/api/wishlist/items/by-product/${productId}/`);
      if (resp.ok || resp.status === 204) {
        setButtonState(btn, false);
        analytics.track('wishlist:remove', { productId });
      }
    }
  } catch {
    // swallow
  }
}

export function initWishlist(): void {
  document.addEventListener('click', async ev => {
    const btn = (ev.target as HTMLElement)?.closest('.wishlist-btn, .wishlist-toggle, .product-card-v2__wishlist, #pdp-wishlist-btn') as WishlistBtn | null;
    if (!btn) return;
    ev.preventDefault();
    const productId = Number(btn.dataset.productId);
    if (!productId) return;
    await toggle(btn, productId);
  });
  loadState();
}

(window as any).Wishlist = { initWishlist };