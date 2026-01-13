/**
 * Help Center JavaScript - Optimized for Performance
 * Includes: Lazy loading, animations, search, and interactions
 */

(function() {
  'use strict';

  // ============================================
  // CONFIGURATION
  // ============================================
  const CONFIG = {
    animationThreshold: 0.15,
    searchDebounceMs: 300,
    lazyLoadRootMargin: '100px',
    scrollOffset: 100
  };

  // ============================================
  // INTERSECTION OBSERVER FOR ANIMATIONS
  // ============================================
  const animationObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('hc-animate-in');
          // Unobserve after animation to save resources
          animationObserver.unobserve(entry.target);
        }
      });
    },
    {
      threshold: CONFIG.animationThreshold,
      rootMargin: '0px 0px -50px 0px'
    }
  );

  // ============================================
  // LAZY LOADING FOR IMAGES
  // ============================================
  const lazyImageObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const img = entry.target;
          
          // Load the actual image
          if (img.dataset.src) {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
          }
          
          if (img.dataset.srcset) {
            img.srcset = img.dataset.srcset;
            img.removeAttribute('data-srcset');
          }
          
          img.classList.add('hc-img-loaded');
          lazyImageObserver.unobserve(img);
        }
      });
    },
    {
      rootMargin: CONFIG.lazyLoadRootMargin
    }
  );

  // ============================================
  // STAGGERED ANIMATION UTILITY
  // ============================================
  function staggerAnimation(elements, baseDelay = 50) {
    elements.forEach((el, index) => {
      el.style.setProperty('--stagger-delay', `${index * baseDelay}ms`);
      animationObserver.observe(el);
    });
  }

  // ============================================
  // SEARCH FUNCTIONALITY
  // ============================================
  class HelpSearch {
    constructor(formSelector, inputSelector) {
      this.form = document.querySelector(formSelector);
      this.input = document.querySelector(inputSelector);
      this.resultsContainer = null;
      this.debounceTimer = null;
      
      if (this.form && this.input) {
        this.init();
      }
    }

    init() {
      // Create live search results container
      this.createResultsContainer();
      
      // Bind events with passive listeners where possible
      this.input.addEventListener('input', this.handleInput.bind(this), { passive: true });
      this.input.addEventListener('focus', this.handleFocus.bind(this), { passive: true });
      this.input.addEventListener('keydown', this.handleKeydown.bind(this));
      
      // Close results on outside click
      document.addEventListener('click', (e) => {
        if (!this.form.contains(e.target)) {
          this.hideResults();
        }
      }, { passive: true });
    }

    createResultsContainer() {
      this.resultsContainer = document.createElement('div');
      this.resultsContainer.className = 'hc-search-results-dropdown';
      this.resultsContainer.setAttribute('aria-live', 'polite');
      this.form.appendChild(this.resultsContainer);
    }

    handleInput() {
      clearTimeout(this.debounceTimer);
      const query = this.input.value.trim();
      
      if (query.length < 2) {
        this.hideResults();
        return;
      }
      
      this.debounceTimer = setTimeout(() => {
        this.performSearch(query);
      }, CONFIG.searchDebounceMs);
    }

    handleFocus() {
      if (this.input.value.trim().length >= 2 && this.resultsContainer.innerHTML) {
        this.showResults();
      }
    }

    handleKeydown(e) {
      if (e.key === 'Escape') {
        this.hideResults();
        this.input.blur();
      } else if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        this.navigateResults(e);
      }
    }

    navigateResults(e) {
      const items = this.resultsContainer.querySelectorAll('.hc-search-result-item');
      if (!items.length) return;
      
      e.preventDefault();
      const current = this.resultsContainer.querySelector('.hc-search-result-item--active');
      let index = current ? Array.from(items).indexOf(current) : -1;
      
      if (e.key === 'ArrowDown') {
        index = Math.min(index + 1, items.length - 1);
      } else {
        index = Math.max(index - 1, 0);
      }
      
      items.forEach(item => item.classList.remove('hc-search-result-item--active'));
      items[index]?.classList.add('hc-search-result-item--active');
      items[index]?.scrollIntoView({ block: 'nearest' });
    }

    async performSearch(query) {
      try {
        this.showLoading();
        
        const response = await fetch(`/help/search/?q=${encodeURIComponent(query)}&ajax=1`, {
          headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        
        if (!response.ok) throw new Error('Search failed');
        
        const data = await response.json();
        this.renderResults(data.results, query);
      } catch (error) {
        console.error('Search error:', error);
        this.hideResults();
      }
    }

    showLoading() {
      this.resultsContainer.innerHTML = `
        <div class="hc-search-loading">
          <div class="hc-search-loading__spinner"></div>
          <span>Searching...</span>
        </div>
      `;
      this.showResults();
    }

    renderResults(results, query) {
      if (!results || !results.length) {
        this.resultsContainer.innerHTML = `
          <div class="hc-search-no-results">
            <span class="material-symbols-rounded">search_off</span>
            <p>No results found for "${this.escapeHtml(query)}"</p>
          </div>
        `;
        this.showResults();
        return;
      }
      
      const html = results.slice(0, 5).map((item, index) => `
        <a href="${item.url}" class="hc-search-result-item ${index === 0 ? 'hc-search-result-item--active' : ''}">
          <span class="material-symbols-rounded hc-search-result-item__icon">${item.icon || 'article'}</span>
          <div class="hc-search-result-item__content">
            <span class="hc-search-result-item__title">${this.highlightQuery(item.title, query)}</span>
            <span class="hc-search-result-item__category">${item.category || 'Help Center'}</span>
          </div>
          <span class="material-symbols-rounded hc-search-result-item__arrow">arrow_forward</span>
        </a>
      `).join('');
      
      this.resultsContainer.innerHTML = html + `
        <a href="/help/search/?q=${encodeURIComponent(query)}" class="hc-search-view-all">
          View all results
          <span class="material-symbols-rounded">arrow_forward</span>
        </a>
      `;
      this.showResults();
    }

    highlightQuery(text, query) {
      const regex = new RegExp(`(${this.escapeRegex(query)})`, 'gi');
      return this.escapeHtml(text).replace(regex, '<mark>$1</mark>');
    }

    escapeHtml(text) {
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
    }

    escapeRegex(string) {
      return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    showResults() {
      this.resultsContainer.classList.add('hc-search-results-dropdown--visible');
    }

    hideResults() {
      this.resultsContainer.classList.remove('hc-search-results-dropdown--visible');
    }
  }

  // ============================================
  // TABLE OF CONTENTS (For Article Pages)
  // ============================================
  class TableOfContents {
    constructor(contentSelector, tocSelector) {
      this.content = document.querySelector(contentSelector);
      this.toc = document.querySelector(tocSelector);
      this.headings = [];
      this.activeId = null;
      
      if (this.content && this.toc) {
        this.init();
      }
    }

    init() {
      this.buildTOC();
      this.setupScrollSpy();
    }

    buildTOC() {
      const headings = this.content.querySelectorAll('h2, h3');
      if (!headings.length) {
        this.toc.style.display = 'none';
        return;
      }
      
      const list = document.createElement('ul');
      list.className = 'hc-toc-list';
      
      headings.forEach((heading, index) => {
        // Generate ID if not present
        if (!heading.id) {
          heading.id = `section-${index + 1}`;
        }
        
        this.headings.push({
          id: heading.id,
          top: heading.offsetTop
        });
        
        const li = document.createElement('li');
        li.className = `hc-toc-item hc-toc-item--${heading.tagName.toLowerCase()}`;
        
        const link = document.createElement('a');
        link.href = `#${heading.id}`;
        link.className = 'hc-toc-link';
        link.textContent = heading.textContent;
        link.addEventListener('click', (e) => {
          e.preventDefault();
          this.scrollToHeading(heading);
        });
        
        li.appendChild(link);
        list.appendChild(li);
      });
      
      const tocList = this.toc.querySelector('.hc-toc-list');
      if (tocList) {
        tocList.replaceWith(list);
      } else {
        this.toc.appendChild(list);
      }
    }

    scrollToHeading(heading) {
      const top = heading.getBoundingClientRect().top + window.pageYOffset - CONFIG.scrollOffset;
      window.scrollTo({ top, behavior: 'smooth' });
      
      // Update URL without triggering scroll
      history.pushState(null, '', `#${heading.id}`);
    }

    setupScrollSpy() {
      let ticking = false;
      
      const updateActiveLink = () => {
        const scrollPos = window.scrollY + CONFIG.scrollOffset + 50;
        let activeHeading = null;
        
        for (let i = this.headings.length - 1; i >= 0; i--) {
          if (scrollPos >= this.headings[i].top) {
            activeHeading = this.headings[i].id;
            break;
          }
        }
        
        if (activeHeading !== this.activeId) {
          this.activeId = activeHeading;
          this.updateActiveState();
        }
        ticking = false;
      };
      
      window.addEventListener('scroll', () => {
        if (!ticking) {
          requestAnimationFrame(updateActiveLink);
          ticking = true;
        }
      }, { passive: true });
      
      // Initial check
      updateActiveLink();
    }

    updateActiveState() {
      const links = this.toc.querySelectorAll('.hc-toc-link');
      links.forEach(link => {
        const isActive = link.getAttribute('href') === `#${this.activeId}`;
        link.classList.toggle('hc-toc-link--active', isActive);
      });
    }
  }

  // ============================================
  // ARTICLE FEEDBACK
  // ============================================
  class ArticleFeedback {
    constructor(containerSelector) {
      this.container = document.querySelector(containerSelector);
      if (this.container) {
        this.init();
      }
    }

    init() {
      const buttons = this.container.querySelectorAll('.hc-feedback-btn');
      buttons.forEach(btn => {
        btn.addEventListener('click', (e) => this.handleFeedback(e));
      });
    }

    async handleFeedback(e) {
      const btn = e.currentTarget;
      const isHelpful = btn.dataset.helpful === 'true';
      const articleSlug = this.container.dataset.articleSlug;
      
      // Prevent double submission
      if (this.container.classList.contains('hc-feedback--submitted')) return;
      
      try {
        const response = await fetch(`/help/article/${articleSlug}/feedback/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.getCSRFToken()
          },
          body: JSON.stringify({ helpful: isHelpful })
        });
        
        if (response.ok) {
          this.showThankYou(isHelpful);
        }
      } catch (error) {
        console.error('Feedback error:', error);
      }
    }

    showThankYou(isHelpful) {
      this.container.classList.add('hc-feedback--submitted');
      this.container.innerHTML = `
        <div class="hc-feedback-thanks">
          <span class="material-symbols-rounded">${isHelpful ? 'sentiment_satisfied' : 'sentiment_dissatisfied'}</span>
          <p>Thank you for your feedback!</p>
          ${!isHelpful ? '<a href="/contact/" class="hc-feedback-contact">Need more help? Contact us</a>' : ''}
        </div>
      `;
    }

    getCSRFToken() {
      return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
             document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '';
    }
  }

  // ============================================
  // SMOOTH REVEAL ANIMATIONS
  // ============================================
  function initAnimations() {
    // Animate category cards with stagger
    const categoryCards = document.querySelectorAll('.hc-category-card');
    staggerAnimation(categoryCards, 75);
    
    // Animate article cards
    const articleCards = document.querySelectorAll('.hc-article-card');
    staggerAnimation(articleCards, 60);
    
    // Animate search results
    const searchResults = document.querySelectorAll('.hc-search-result');
    staggerAnimation(searchResults, 50);
    
    // Animate sections
    const sections = document.querySelectorAll('.hc-section-header, .hc-featured, .hc-popular, .hc-recent, .hc-quick-links, .hc-cta');
    sections.forEach(section => animationObserver.observe(section));
    
    // Hero animation - immediate
    const heroContent = document.querySelector('.hc-hero__content');
    if (heroContent) {
      heroContent.classList.add('hc-animate-in');
    }
  }

  // ============================================
  // LAZY LOAD IMAGES
  // ============================================
  function initLazyLoading() {
    const lazyImages = document.querySelectorAll('img[data-src], img[loading="lazy"]');
    lazyImages.forEach(img => {
      // For native lazy loading support
      if ('loading' in HTMLImageElement.prototype && img.loading === 'lazy') {
        // Browser handles it natively
        return;
      }
      lazyImageObserver.observe(img);
    });
  }

  // ============================================
  // SHARE FUNCTIONALITY
  // ============================================
  function initShareButtons() {
    const shareButtons = document.querySelectorAll('.hc-share-btn');
    
    shareButtons.forEach(btn => {
      btn.addEventListener('click', async (e) => {
        e.preventDefault();
        const platform = btn.dataset.platform;
        const url = window.location.href;
        const title = document.title;
        
        if (platform === 'copy') {
          try {
            await navigator.clipboard.writeText(url);
            showToast('Link copied to clipboard!');
          } catch (err) {
            // Fallback for older browsers
            const input = document.createElement('input');
            input.value = url;
            document.body.appendChild(input);
            input.select();
            document.execCommand('copy');
            document.body.removeChild(input);
            showToast('Link copied to clipboard!');
          }
        } else if (platform === 'native' && navigator.share) {
          try {
            await navigator.share({ title, url });
          } catch (err) {
            // User cancelled or error
          }
        } else {
          const shareUrls = {
            twitter: `https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(title)}`,
            facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`,
            linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`,
            email: `mailto:?subject=${encodeURIComponent(title)}&body=${encodeURIComponent(url)}`
          };
          
          if (shareUrls[platform]) {
            window.open(shareUrls[platform], '_blank', 'width=600,height=400');
          }
        }
      });
    });
  }

  // ============================================
  // TOAST NOTIFICATIONS
  // ============================================
  function showToast(message, duration = 3000) {
    const existing = document.querySelector('.hc-toast');
    if (existing) existing.remove();
    
    const toast = document.createElement('div');
    toast.className = 'hc-toast';
    toast.innerHTML = `
      <span class="material-symbols-rounded">check_circle</span>
      <span>${message}</span>
    `;
    
    document.body.appendChild(toast);
    
    // Trigger animation
    requestAnimationFrame(() => {
      toast.classList.add('hc-toast--visible');
    });
    
    setTimeout(() => {
      toast.classList.remove('hc-toast--visible');
      setTimeout(() => toast.remove(), 300);
    }, duration);
  }

  // ============================================
  // PERFORMANCE: DEFER NON-CRITICAL OPERATIONS
  // ============================================
  function whenIdle(callback) {
    if ('requestIdleCallback' in window) {
      requestIdleCallback(callback);
    } else {
      setTimeout(callback, 100);
    }
  }

  // ============================================
  // INITIALIZE
  // ============================================
  function init() {
    // Critical - run immediately
    initAnimations();
    
    // Initialize search
    new HelpSearch('.hc-search__form', '.hc-search__input');
    new HelpSearch('.hc-inline-search', '.hc-inline-search__input');
    
    // Initialize TOC for article pages
    new TableOfContents('.hc-article__body', '.hc-article__toc');
    
    // Initialize feedback
    new ArticleFeedback('.hc-feedback');
    
    // Non-critical - defer
    whenIdle(() => {
      initLazyLoading();
      initShareButtons();
    });
  }

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Expose for external use if needed
  window.HelpCenter = {
    showToast,
    HelpSearch,
    TableOfContents,
    ArticleFeedback
  };
})();
