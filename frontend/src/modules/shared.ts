type ApiResponse<T = any> = { ok: boolean; status: number; body: T };

function getCsrf(): string {
  // First try to find csrftoken in cookies
  const match = document.cookie.match(/(?:^|;\s*)csrftoken\s*=\s*([^;]+)/);
  if (match && match[1]) {
    return match[1];
  }
  
  // Fallback: try to find it in a meta tag
  const metaToken = document.querySelector('meta[name="csrf-token"]') as HTMLMetaElement;
  if (metaToken?.content) {
    return metaToken.content;
  }
  
  console.warn('CSRF token not found');
  return '';
}

export const api = {
  async get(url: string): Promise<ApiResponse> {
    const resp = await fetch(url, { 
      credentials: 'include',
      headers: { 
        'X-CSRFToken': getCsrf(),
        'X-Requested-With': 'XMLHttpRequest' 
      } 
    });
    const body = await parseBody(resp);
    return { ok: resp.ok, status: resp.status, body };
  },
  async post(url: string, data?: any): Promise<ApiResponse> {
    const resp = await fetch(url, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrf(), 'X-Requested-With': 'XMLHttpRequest' },
      body: JSON.stringify(data || {})
    });
    const body = await parseBody(resp);
    return { ok: resp.ok, status: resp.status, body };
  },
  async del(url: string): Promise<ApiResponse> {
    const resp = await fetch(url, {
      method: 'DELETE',
      credentials: 'include',
      headers: { 'X-CSRFToken': getCsrf(), 'X-Requested-With': 'XMLHttpRequest' }
    });
    const body = await parseBody(resp);
    return { ok: resp.ok, status: resp.status, body };
  }
};

async function parseBody(resp: Response): Promise<any> {
  const ct = resp.headers.get('content-type') || '';
  if (ct.includes('application/json')) return resp.json();
  return resp.text();
}

export const analytics = {
  track(eventName: string, payload?: Record<string, any>) {
    if (console && console.debug) console.debug('[analytics]', eventName, payload || {});
  }
};

export const flags = {
  isEnabled(key: string): boolean {
    return Boolean(localStorage.getItem('flag:' + key));
  }
};
