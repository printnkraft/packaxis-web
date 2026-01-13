import { api } from './shared';

type Address = {
  id: number;
  first_name: string;
  last_name: string;
  company?: string;
  address1: string;
  address2?: string;
  city: string;
  province: string;
  postal_code: string;
  country?: string;
  phone?: string;
  is_default_shipping?: boolean;
  is_default_billing?: boolean;
};

const fallbackProvinces = [
  { code: 'AB', name: 'Alberta' }, { code: 'BC', name: 'British Columbia' }, { code: 'MB', name: 'Manitoba' },
  { code: 'NB', name: 'New Brunswick' }, { code: 'NL', name: 'Newfoundland and Labrador' }, { code: 'NS', name: 'Nova Scotia' },
  { code: 'NT', name: 'Northwest Territories' }, { code: 'NU', name: 'Nunavut' }, { code: 'ON', name: 'Ontario' },
  { code: 'PE', name: 'Prince Edward Island' }, { code: 'QC', name: 'Quebec' }, { code: 'SK', name: 'Saskatchewan' }, { code: 'YT', name: 'Yukon' }
];

function renderAddressCards(addresses: Address[]): string {
  return `
    <div class="addresses-list-grid">
      ${addresses.map(a => `
        <div class="address-tile">
          <div class="address-tile__header">
            <strong class="address-tile__name">${a.first_name} ${a.last_name}</strong>
            <span class="address-tile__meta">${flagText(a)}</span>
          </div>
          <div class="address-tile__body">
            ${a.address1}${a.address2 ? '<br>'+a.address2 : ''}<br>
            ${a.city}, ${a.province} ${a.postal_code}<br>
            ${a.country || 'CA'}
          </div>
          <div class="address-tile__actions">
            <button class="btn btn-secondary btn-ghost addr-edit" data-id="${a.id}">Edit</button>
            <button class="btn btn-danger addr-delete" data-id="${a.id}">Delete</button>
            ${a.is_default_shipping ? '' : `<button class="btn btn-soft-success addr-default-ship" data-id="${a.id}">Set Default Shipping</button>`}
            ${a.is_default_billing ? '' : `<button class="btn btn-soft-accent addr-default-bill" data-id="${a.id}">Set Default Billing</button>`}
          </div>
        </div>
      `).join('')}
    </div>
  `;
}

function flagText(a: Address): string {
  const flags: string[] = [];
  if (a.is_default_shipping) flags.push('Default Shipping');
  if (a.is_default_billing) flags.push('Default Billing');
  return flags.join(' • ');
}

async function populateProvinces(): Promise<void> {
  const select = document.getElementById('province') as HTMLSelectElement | null;
  if (!select) return;
  const res = await api.get('/api/checkout/provinces/');
  const provinces = (res.ok && res.body?.provinces) ? res.body.provinces : fallbackProvinces;
  select.innerHTML = provinces.map((p: any) => `<option value="${p.code}">${p.name}</option>`).join('');
}

async function fetchAddresses(): Promise<void> {
  const container = document.getElementById('addresses-list');
  if (!container) return;
  try {
    const res = await api.get('/api/accounts/addresses/');
    if (!res.ok) {
      container.innerHTML = '<div class="addresses-empty"><p>No addresses or not authenticated.</p></div>';
      return;
    }
    const items: Address[] = Array.isArray(res.body) ? res.body : (res.body?.results || []);
    if (!items.length) {
      container.innerHTML = '<div class="addresses-empty"><p>No addresses yet. Add one using the form.</p></div>';
      return;
    }
    container.innerHTML = renderAddressCards(items);
    bindListActions(items);
  } catch (e) {
    container.innerHTML = '<div class="addresses-empty addresses-empty--error"><p>Failed to load addresses.</p></div>';
  }
}

function bindListActions(addresses: Address[]) {
  const byId = new Map(addresses.map(a => [String(a.id), a]));
  document.querySelectorAll('.addr-edit').forEach(btn => {
    btn.addEventListener('click', () => {
      const a = byId.get(String((btn as HTMLElement).dataset.id));
      if (a) fillForm(a);
    });
  });
  document.querySelectorAll('.addr-delete').forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = (btn as HTMLElement).dataset.id;
      if (!id || !confirm('Delete this address?')) return;
      await api.del(`/api/accounts/addresses/${id}/`);
      fetchAddresses();
    });
  });
  document.querySelectorAll('.addr-default-ship').forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = (btn as HTMLElement).dataset.id;
      if (!id) return;
      await api.post(`/api/accounts/addresses/${id}/`, { is_default_shipping: true });
      fetchAddresses();
    });
  });
  document.querySelectorAll('.addr-default-bill').forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = (btn as HTMLElement).dataset.id;
      if (!id) return;
      await api.post(`/api/accounts/addresses/${id}/`, { is_default_billing: true });
      fetchAddresses();
    });
  });
}

function fillForm(a: Address) {
  setText('form-title', 'Edit Address');
  setText('form-subtitle', 'Update the fields and save.');
  setVal('address-id', String(a.id));
  setVal('first_name', a.first_name);
  setVal('last_name', a.last_name);
  setVal('company', a.company || '');
  setVal('address1', a.address1);
  setVal('address2', a.address2 || '');
  setVal('city', a.city);
  setVal('province', a.province);
  setVal('postal_code', a.postal_code);
  setVal('country', a.country || 'CA');
  setVal('phone', a.phone || '');
  setChecked('is_default_shipping', !!a.is_default_shipping);
  setChecked('is_default_billing', !!a.is_default_billing);
}

function resetForm() {
  setText('form-title', 'Add New Address');
  setText('form-subtitle', 'Fill in the details below.');
  ['address-id','first_name','last_name','company','address1','address2','city','postal_code','phone'].forEach(id=>setVal(id,''));
  setVal('province','ON');
  setVal('country','CA');
  setChecked('is_default_shipping', false);
  setChecked('is_default_billing', false);
}

function setText(id: string, text: string) { const el = document.getElementById(id); if (el) el.textContent = text; }
function setVal(id: string, val: string) { const el = document.getElementById(id) as HTMLInputElement | HTMLSelectElement | null; if (el) el.value = val; }
function setChecked(id: string, val: boolean) { const el = document.getElementById(id) as HTMLInputElement | null; if (el) el.checked = !!val; }

async function saveAddress(ev: Event) {
  ev.preventDefault();
  const id = (document.getElementById('address-id') as HTMLInputElement | null)?.value;
  const payload = {
    first_name: (document.getElementById('first_name') as HTMLInputElement).value.trim(),
    last_name: (document.getElementById('last_name') as HTMLInputElement).value.trim(),
    company: (document.getElementById('company') as HTMLInputElement).value.trim(),
    address1: (document.getElementById('address1') as HTMLInputElement).value.trim(),
    address2: (document.getElementById('address2') as HTMLInputElement).value.trim(),
    city: (document.getElementById('city') as HTMLInputElement).value.trim(),
    province: (document.getElementById('province') as HTMLSelectElement).value,
    postal_code: (document.getElementById('postal_code') as HTMLInputElement).value.trim(),
    country: (document.getElementById('country') as HTMLSelectElement).value,
    phone: (document.getElementById('phone') as HTMLInputElement).value.trim(),
    is_default_shipping: (document.getElementById('is_default_shipping') as HTMLInputElement).checked,
    is_default_billing: (document.getElementById('is_default_billing') as HTMLInputElement).checked
  };
  const url = id ? `/api/accounts/addresses/${id}/` : '/api/accounts/addresses/';
  const res = await api.post(url, payload);
  const msg = document.getElementById('form-message') as HTMLElement | null;
  if (msg) {
    msg.style.display = 'block';
    msg.style.color = res.ok ? '' : '#cc0000';
    msg.textContent = res.ok ? 'Saved successfully.' : 'Failed to save address.';
    setTimeout(() => { msg.style.display = 'none'; msg.style.color = ''; }, res.ok ? 2000 : 2500);
  }
  if (res.ok) {
    resetForm();
    fetchAddresses();
  }
}

export function initAddresses(): void {
  if (!document.getElementById('address-form')) return;
  populateProvinces();
  fetchAddresses();
  const form = document.getElementById('address-form');
  if (form) form.addEventListener('submit', saveAddress);
  const resetBtn = document.getElementById('reset-btn');
  if (resetBtn) resetBtn.addEventListener('click', resetForm);
}

(window as any).Addresses = { initAddresses };
