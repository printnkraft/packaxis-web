// Printify-inspired micro-interactions (original)
(function () {
  const prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const hasNoAnimate = () => document.documentElement.classList.contains('no-animate') || document.body.classList.contains('no-animate');

  // IntersectionObserver for on-scroll reveals
  const reveal = () => {
    // Auto-opt-in common blocks for animation if not explicitly disabled
    document.querySelectorAll('.card, .product-card, .feature-card, .industry-card, .service-card, .testimonial-card, .sidebar-card')
      .forEach(el => { if (!el.classList.contains('no-animate')) el.classList.add('animate-on-scroll'); });

    const items = document.querySelectorAll('.animate-on-scroll');
    if (prefersReduced || hasNoAnimate()) {
      items.forEach(el => el.classList.add('visible'));
      return;
    }
    if (!('IntersectionObserver' in window) || items.length === 0) {
      // Fallback: reveal immediately
      items.forEach(el => el.classList.add('visible'));
      return;
    }
    const io = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.1 });

    items.forEach(el => io.observe(el));
  };

  // Progress bars: <div class="progress" data-progress="72"><div class="progress__bar"></div></div>
  const initProgressBars = () => {
    document.querySelectorAll('.progress').forEach(wrapper => {
      const pct = parseFloat(wrapper.getAttribute('data-progress') || '0');
      let bar = wrapper.querySelector('.progress__bar');
      if (!bar) {
        bar = document.createElement('div');
        bar.className = 'progress__bar';
        wrapper.appendChild(bar);
      }
      requestAnimationFrame(() => {
        bar.style.width = Math.max(0, Math.min(100, pct)) + '%';
      });
    });
  };

  // Subtle ripple for .btn
  const initRipple = () => {
    if (prefersReduced || hasNoAnimate()) return;
    const addRipple = (e) => {
      const btn = e.currentTarget;
      const circle = document.createElement('span');
      const diameter = Math.max(btn.clientWidth, btn.clientHeight);
      const radius = diameter / 2;
      circle.style.width = circle.style.height = `${diameter}px`;
      circle.style.left = `${e.clientX - (btn.getBoundingClientRect().left + radius)}px`;
      circle.style.top = `${e.clientY - (btn.getBoundingClientRect().top + radius)}px`;
      circle.classList.add('ripple');
      const old = btn.getElementsByClassName('ripple')[0];
      if (old) old.remove();
      btn.appendChild(circle);
      setTimeout(() => circle.remove(), 600);
    };

    // CSS injection removed per redesign request.

    document.querySelectorAll('.btn').forEach(btn => {
      btn.addEventListener('click', addRipple);
    });
  };

  // Initialize on DOM ready
  const init = () => { reveal(); initProgressBars(); initRipple(); };
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else { init(); }
})();
