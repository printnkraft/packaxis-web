(function(){
  function getCsrf(){
    const match = document.cookie.match('(^|;)\\s*csrftoken\\s*=\\s*([^;]+)');
    return match ? match[2] : '';
  }

  async function request(url, options){
    const headers = Object.assign({ 'X-Requested-With': 'XMLHttpRequest' }, options.headers || {});
    if (options.method && options.method !== 'GET' && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    }
    if (options.method && options.method !== 'GET') {
      headers['X-CSRFToken'] = headers['X-CSRFToken'] || getCsrf();
    }
    const resp = await fetch(url, Object.assign({}, options, { headers }));
    const contentType = resp.headers.get('content-type') || '';
    const body = contentType.includes('application/json') ? await resp.json() : await resp.text();
    return { ok: resp.ok, status: resp.status, body };
  }

  const api = {
    get: (url) => request(url, { method: 'GET' }),
    post: (url, data) => request(url, { method: 'POST', body: JSON.stringify(data || {}) }),
    patch: (url, data) => request(url, { method: 'PATCH', body: JSON.stringify(data || {}) }),
    del: (url) => request(url, { method: 'DELETE' })
  };

  const analytics = {
    track(eventName, payload){
      if (window.console && console.debug) {
        console.debug('[analytics]', eventName, payload || {});
      }
    }
  };

  const flags = {
    isEnabled(key){
      return Boolean(window.localStorage.getItem('flag:' + key));
    }
  };

  window.App = Object.assign({}, window.App, { api, analytics, flags });
})();
