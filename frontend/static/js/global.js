/**
 * =============================================================================
 * PACKAXIS - Global Application Module
 * =============================================================================
 * Core application class providing CSRF management, API communication,
 * notifications, and global event handling
 * @module global
 * @version 2.0.0
 * @author Packaxis Development Team
 * =============================================================================
 */

/**
 * =============================================================================
 * ProductSearch - Real-Time In-Grid Product Filtering
 * =============================================================================
 * Filters products directly in the product grid as user types:
 * - Real-time filtering with debouncing (300ms)
 * - Updates product grid via AJAX
 * - Search highlighting in results
 * - Loading states and smooth transitions
 * - URL state management
 * - Performance optimized (<500ms response target)
 * =============================================================================
 */
class ProductSearch {
  /**
   * Initialize ProductSearch
   * @param {Object} config - Configuration options
   */
  constructor(config = {}) {
    this.config = {
      searchAjaxUrl: config.searchAjaxUrl || '/products/search/',
      debounceDelay: config.debounceDelay || 300,
      minChars: config.minChars || 1,
      ...config
    };
    
    // Current state
    this.currentFilters = config.currentFilters || {
      search: '',
      category: '',
      sort: 'newest',
      page: 1
    };
    
    // DOM elements
    this.elements = {};
    this.debounceTimer = null;
    this.isLoading = false;
    
    // Bind methods
    this.handleSearchInput = this.handleSearchInput.bind(this);
    this.handleSortChange = this.handleSortChange.bind(this);
    this.handleKeydown = this.handleKeydown.bind(this);
    this.handleCategoryClick = this.handleCategoryClick.bind(this);
    
    this.init();
  }
  
  /**
   * Initialize all event listeners and DOM references
   */
  init() {
    // Cache DOM elements
    this.elements = {
      searchForm: document.getElementById('products-search-form'),
      searchInput: document.getElementById('products-search-input'),
      searchClearBtn: document.getElementById('search-clear-btn'),
      sortSelect: document.getElementById('sort-select'),
      productGrid: document.getElementById('product-grid'),
      productsCount: document.getElementById('products-count'),
      loadingOverlay: document.getElementById('products-loading'),
      filterLinks: document.querySelectorAll('.filter-link[data-category]'),
      currentSearchQuery: document.getElementById('current-search-query'),
      pagination: document.querySelector('.pagination'),
      productsFooter: document.querySelector('.products-footer'),
      productsEmpty: document.querySelector('.products-empty'),
      categoryFilterDisplay: document.querySelector('[data-filter-type="category"]'),
      toolbarInfo: document.querySelector('.products-toolbar__info')
    };
    
    if (!this.elements.searchInput) return;
    
    // Search input - real-time filtering
    this.elements.searchInput.addEventListener('input', this.handleSearchInput);
    this.elements.searchInput.addEventListener('keydown', this.handleKeydown);
    
    // Clear search button
    if (this.elements.searchClearBtn) {
      this.elements.searchClearBtn.addEventListener('click', () => this.clearSearch());
    }
    
    // Sort dropdown
    if (this.elements.sortSelect) {
      this.elements.sortSelect.addEventListener('change', this.handleSortChange);
    }
    
    // Category filter links - AJAX filtering
    this.elements.filterLinks.forEach(link => {
      link.addEventListener('click', this.handleCategoryClick);
    });
    
    // Prevent form submission - use AJAX instead
    if (this.elements.searchForm) {
      this.elements.searchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        this.performSearch();
      });
    }
  }
  
  /**
   * Handle category click - filter products via AJAX
   * @param {Event} e - Click event
   */
  handleCategoryClick(e) {
    e.preventDefault();
    
    const link = e.currentTarget;
    const category = link.dataset.category;
    
    // Update current filters
    this.currentFilters.category = category;
    this.currentFilters.page = 1; // Reset to page 1
    
    // Update active state on links
    this.updateCategoryActiveState(category);
    
    // Perform search with new category
    this.performSearch();
  }
  
  /**
   * Update active state on category filter links
   * @param {string} activeCategory - The active category slug
   */
  updateCategoryActiveState(activeCategory) {
    this.elements.filterLinks.forEach(link => {
      const isActive = link.dataset.category === activeCategory;
      link.classList.toggle('filter-link--active', isActive);
      link.setAttribute('aria-current', isActive ? 'page' : 'false');
    });
  }
  
  /**
   * Handle search input with debouncing - filters products in grid
   * @param {Event} e - Input event
   */
  handleSearchInput(e) {
    const query = e.target.value.trim();
    
    // Clear previous timer
    clearTimeout(this.debounceTimer);
    
    // Show/hide clear button
    this.toggleClearButton(query.length > 0);
    
    // Update current filters
    this.currentFilters.search = query;
    this.currentFilters.page = 1; // Reset to page 1
    
    // Debounce the search
    this.debounceTimer = setTimeout(() => {
      this.performSearch();
    }, this.config.debounceDelay);
  }
  
  /**
   * Perform search and update product grid
   */
  async performSearch() {
    const query = this.currentFilters.search;
    
    // Show loading state
    this.showLoading(true);
    
    try {
      // Build URL with current filters
      const params = new URLSearchParams();
      if (query) params.set('search', query);
      if (this.currentFilters.category) params.set('category', this.currentFilters.category);
      if (this.currentFilters.sort) params.set('sort', this.currentFilters.sort);
      params.set('page', this.currentFilters.page);
      
      const response = await fetch(`${this.config.searchAjaxUrl}?${params.toString()}`);
      if (!response.ok) throw new Error('Search request failed');
      
      const data = await response.json();
      this.renderProducts(data, query);
      this.updateURL();
      
    } catch (error) {
      console.error('Search error:', error);
      window.app?.showError('Search failed. Please try again.');
    } finally {
      this.showLoading(false);
    }
  }
  
  /**
   * Render products in the grid
   * @param {Object} data - Search response data
   * @param {string} query - Search query for highlighting
   */
  renderProducts(data, query) {
    const { products, pagination, filters } = data;
    
    // Update products count
    if (this.elements.productsCount) {
      const count = pagination.total_count;
      this.elements.productsCount.textContent = `${count} product${count !== 1 ? 's' : ''}`;
    }
    
    // Update "All Products" count in sidebar
    const allProductsLink = document.querySelector('.filter-link[data-category=""]');
    if (allProductsLink) {
      const countSpan = allProductsLink.querySelector('.filter-link__count');
      if (countSpan && !this.currentFilters.category && !this.currentFilters.search) {
        countSpan.textContent = pagination.total_count;
      }
    }
    
    // Update toolbar filter displays
    this.updateToolbarFilters(filters, pagination);
    
    // Update current search query display
    if (this.elements.currentSearchQuery && query) {
      this.elements.currentSearchQuery.textContent = query;
    }
    
    // Handle empty state
    if (!products || products.length === 0) {
      this.renderEmptyState(query);
      return;
    }
    
    // Hide empty state if visible
    if (this.elements.productsEmpty) {
      this.elements.productsEmpty.style.display = 'none';
    }
    
    // Show grid
    if (this.elements.productGrid) {
      this.elements.productGrid.style.display = '';
    }
    
    // Render product cards
    let html = '';
    products.forEach((product, index) => {
      const highlightedName = this.highlightMatch(product.name, query);
      const highlightedDesc = this.highlightMatch(product.description, query);
      
      html += `
        <article class="product-card-v2" role="listitem" style="animation-delay: ${index * 50}ms; opacity: 0; transform: translateY(20px);">
          <a href="${product.url}" class="product-card-v2__link" aria-label="View ${this.escapeHtml(product.name)} details">
            <div class="product-card-v2__image">
              ${product.image_url 
                ? `<img src="${product.image_url}" alt="${this.escapeHtml(product.name)}" loading="lazy" decoding="async">`
                : `<div class="product-card-v2__placeholder"><span class="material-symbols-rounded">inventory_2</span></div>`
              }
              <div class="product-card-v2__badges">
                ${product.in_stock 
                  ? '<span class="product-badge product-badge--success">In Stock</span>'
                  : '<span class="product-badge product-badge--danger">Out of Stock</span>'
                }
              </div>
              <div class="product-card-v2__overlay">
                <button class="product-card-v2__quick-view" aria-label="Quick view ${this.escapeHtml(product.name)}">
                  <span class="material-symbols-rounded">visibility</span>
                </button>
                <button class="product-card-v2__wishlist" data-product-id="${product.id}" aria-label="Add ${this.escapeHtml(product.name)} to wishlist">
                  <span class="material-symbols-rounded">favorite_border</span>
                </button>
              </div>
            </div>
            <div class="product-card-v2__content">
              ${product.category?.name ? `<span class="product-card-v2__category">${this.escapeHtml(product.category.name)}</span>` : ''}
              <h3 class="product-card-v2__title">${highlightedName}</h3>
              <p class="product-card-v2__description">${highlightedDesc}</p>
              <div class="product-card-v2__footer">
                <div class="product-card-v2__price">
                  <span class="product-card-v2__price-value">$${product.price}</span>
                  <span class="product-card-v2__price-unit">/unit</span>
                </div>
              </div>
            </div>
          </a>
          <button 
            data-add-to-cart
            data-product-id="${product.id}"
            data-product-name="${this.escapeHtml(product.name)}"
            data-price="${product.price}"
            data-image="${product.image_url || ''}"
            class="product-card-v2__cart-btn" 
            ${!product.in_stock ? 'disabled aria-disabled="true"' : ''}
            aria-label="Add ${this.escapeHtml(product.name)} to cart">
            <span class="material-symbols-rounded">add_shopping_cart</span>
            <span>Add to Cart</span>
          </button>
        </article>`;
    });
    
    if (this.elements.productGrid) {
      this.elements.productGrid.innerHTML = html;
      
      // Animate cards in
      requestAnimationFrame(() => {
        const cards = this.elements.productGrid.querySelectorAll('.product-card-v2');
        cards.forEach((card, i) => {
          setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
          }, i * 50);
        });
      });
    }
    
    // Update pagination
    this.renderPagination(pagination);
    
    // Update footer
    this.updateFooter(pagination);
  }
  
  /**
   * Render empty state
   * @param {string} query - Search query
   */
  renderEmptyState(query) {
    if (this.elements.productGrid) {
      this.elements.productGrid.style.display = 'none';
    }
    
    if (this.elements.pagination) {
      this.elements.pagination.style.display = 'none';
    }
    
    // Create or show empty state
    const emptyHtml = `
      <div class="products-empty" role="status">
        <div class="products-empty__icon">
          <span class="material-symbols-rounded">search_off</span>
        </div>
        <h2 class="products-empty__title">No Products Found</h2>
        <p class="products-empty__text">${query ? `No products match your search "${this.escapeHtml(query)}".` : 'No products available yet.'}</p>
        <button type="button" class="btn btn-primary" onclick="window.productSearch?.clearSearch()">
          <span class="material-symbols-rounded">arrow_back</span>
          Clear Search
        </button>
      </div>`;
    
    if (this.elements.productsEmpty) {
      this.elements.productsEmpty.outerHTML = emptyHtml;
      this.elements.productsEmpty = document.querySelector('.products-empty');
    } else {
      // Insert after product grid
      if (this.elements.productGrid) {
        this.elements.productGrid.insertAdjacentHTML('afterend', emptyHtml);
        this.elements.productsEmpty = document.querySelector('.products-empty');
      }
    }
  }
  
  /**
   * Render pagination
   * @param {Object} pagination - Pagination data
   */
  renderPagination(pagination) {
    if (!this.elements.pagination) return;
    
    if (pagination.total_pages <= 1) {
      this.elements.pagination.style.display = 'none';
      return;
    }
    
    this.elements.pagination.style.display = '';
    
    const { current_page, total_pages, total_count, page_range, has_previous, has_next } = pagination;
    
    let html = `
      <div class="pagination__info">
        Showing page ${current_page} of ${total_pages} (${total_count} products)
      </div>
      <ul class="pagination__list">
        <li>
          <button class="pagination__link pagination__link--prev ${!has_previous ? 'pagination__link--disabled' : ''}" 
            ${!has_previous ? 'disabled' : ''} 
            data-page="${current_page - 1}" aria-label="Go to previous page">
            <span class="material-symbols-rounded">chevron_left</span>
          </button>
        </li>`;
    
    // First page
    if (page_range[0] > 1) {
      html += `<li><button class="pagination__link" data-page="1">1</button></li>`;
      if (page_range[0] > 2) {
        html += `<li><span class="pagination__ellipsis">…</span></li>`;
      }
    }
    
    // Page numbers
    page_range.forEach(pageNum => {
      html += `<li>
        <button class="pagination__link ${pageNum === current_page ? 'pagination__link--active' : ''}" 
          data-page="${pageNum}" ${pageNum === current_page ? 'aria-current="page"' : ''}>
          ${pageNum}
        </button>
      </li>`;
    });
    
    // Last page
    if (page_range[page_range.length - 1] < total_pages) {
      if (page_range[page_range.length - 1] < total_pages - 1) {
        html += `<li><span class="pagination__ellipsis">…</span></li>`;
      }
      html += `<li><button class="pagination__link" data-page="${total_pages}">${total_pages}</button></li>`;
    }
    
    html += `
        <li>
          <button class="pagination__link pagination__link--next ${!has_next ? 'pagination__link--disabled' : ''}" 
            ${!has_next ? 'disabled' : ''} 
            data-page="${current_page + 1}" aria-label="Go to next page">
            <span class="material-symbols-rounded">chevron_right</span>
          </button>
        </li>
      </ul>`;
    
    this.elements.pagination.innerHTML = html;
    
    // Add click handlers
    this.elements.pagination.querySelectorAll('[data-page]').forEach(btn => {
      btn.addEventListener('click', () => {
        const page = parseInt(btn.dataset.page);
        if (page && page !== this.currentFilters.page) {
          this.currentFilters.page = page;
          this.performSearch();
          // Scroll to top of grid
          this.elements.productGrid?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    });
  }
  
  /**
   * Update footer text
   * @param {Object} pagination - Pagination data
   */
  updateFooter(pagination) {
    if (this.elements.productsFooter) {
      const text = pagination.total_pages > 1 
        ? `Page ${pagination.current_page} of ${pagination.total_pages}`
        : `Showing all ${pagination.total_count} product${pagination.total_count !== 1 ? 's' : ''}`;
      this.elements.productsFooter.innerHTML = `<p class="products-footer__text">${text}</p>`;
    }
  }
  
  /**
   * Handle keyboard events
   * @param {KeyboardEvent} e - Keydown event
   */
  handleKeydown(e) {
    if (e.key === 'Enter') {
      e.preventDefault();
      clearTimeout(this.debounceTimer);
      this.performSearch();
    } else if (e.key === 'Escape') {
      this.clearSearch();
    }
  }
  
  /**
   * Highlight matching text
   * @param {string} text - Text to highlight
   * @param {string} query - Search query
   * @returns {string} HTML with highlighted matches
   */
  highlightMatch(text, query) {
    if (!query || !text) return this.escapeHtml(text || '');
    const regex = new RegExp(`(${this.escapeRegex(query)})`, 'gi');
    return this.escapeHtml(text).replace(regex, '<mark class="search-highlight">$1</mark>');
  }
  
  /**
   * Escape HTML entities
   * @param {string} str - String to escape
   * @returns {string} Escaped string
   */
  escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }
  
  /**
   * Escape regex special characters
   * @param {string} str - String to escape
   * @returns {string} Escaped string
   */
  escapeRegex(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }
  
  /**
   * Toggle clear button visibility
   * @param {boolean} show - Whether to show button
   */
  toggleClearButton(show) {
    // Create clear button if it doesn't exist
    if (!this.elements.searchClearBtn && show) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'search-clear-btn';
      btn.id = 'search-clear-btn';
      btn.setAttribute('aria-label', 'Clear search');
      btn.innerHTML = '<span class="material-symbols-rounded">close</span>';
      btn.addEventListener('click', () => this.clearSearch());
      this.elements.searchInput.parentNode.appendChild(btn);
      this.elements.searchClearBtn = btn;
    }
    
    if (this.elements.searchClearBtn) {
      this.elements.searchClearBtn.style.display = show ? 'flex' : 'none';
    }
  }
  
  /**
   * Clear search and reload all products
   */
  clearSearch() {
    this.elements.searchInput.value = '';
    this.currentFilters.search = '';
    this.currentFilters.page = 1;
    this.toggleClearButton(false);
    this.performSearch();
    this.elements.searchInput.focus();
  }
  
  /**
   * Handle sort change
   * @param {Event} e - Change event
   */
  handleSortChange(e) {
    this.currentFilters.sort = e.target.value;
    this.currentFilters.page = 1;
    this.performSearch();
  }
  
  /**
   * Update URL with current filters (without page reload)
   */
  updateURL() {
    const url = new URL(window.location.href);
    
    if (this.currentFilters.search) {
      url.searchParams.set('search', this.currentFilters.search);
    } else {
      url.searchParams.delete('search');
    }
    
    if (this.currentFilters.category) {
      url.searchParams.set('category', this.currentFilters.category);
    } else {
      url.searchParams.delete('category');
    }
    
    if (this.currentFilters.sort && this.currentFilters.sort !== 'newest') {
      url.searchParams.set('sort', this.currentFilters.sort);
    } else {
      url.searchParams.delete('sort');
    }
    
    if (this.currentFilters.page > 1) {
      url.searchParams.set('page', this.currentFilters.page);
    } else {
      url.searchParams.delete('page');
    }
    
    window.history.replaceState({}, '', url);
  }
  
  /**
   * Update toolbar filter display badges
   * @param {Object} filters - Current active filters
   * @param {Object} pagination - Pagination data
   */
  updateToolbarFilters(filters, pagination) {
    if (!this.elements.toolbarInfo) return;
    
    // Get the count element
    let countEl = this.elements.productsCount;
    if (!countEl) {
      countEl = this.elements.toolbarInfo.querySelector('.products-toolbar__count');
    }
    
    // Build filter badges HTML
    let filtersHtml = '';
    
    // Category filter badge
    if (filters?.category) {
      // Use category_name from response, fallback to finding it in DOM
      let categoryName = filters.category_name;
      if (!categoryName) {
        const categoryLink = document.querySelector(`.filter-link[data-category="${filters.category}"]`);
        categoryName = categoryLink?.querySelector('.filter-link__text')?.textContent || filters.category;
      }
      
      filtersHtml += `
        <span class="products-toolbar__filter" data-filter-type="category">
          in <strong>${this.escapeHtml(categoryName)}</strong>
          <button type="button" class="products-toolbar__clear" aria-label="Clear category filter" data-clear-filter="category">
            <span class="material-symbols-rounded">close</span>
          </button>
        </span>`;
    }
    
    // Search filter badge
    if (filters?.search) {
      filtersHtml += `
        <span class="products-toolbar__filter" data-filter-type="search">
          matching "<strong id="current-search-query">${this.escapeHtml(filters.search)}</strong>"
          <button type="button" class="products-toolbar__clear" aria-label="Clear search" data-clear-filter="search">
            <span class="material-symbols-rounded">close</span>
          </button>
        </span>`;
    }
    
    // Update toolbar info
    const countHtml = `<span class="products-toolbar__count" id="products-count">${pagination.total_count} product${pagination.total_count !== 1 ? 's' : ''}</span>`;
    this.elements.toolbarInfo.innerHTML = countHtml + filtersHtml;
    
    // Re-cache the count element
    this.elements.productsCount = document.getElementById('products-count');
    this.elements.currentSearchQuery = document.getElementById('current-search-query');
    
    // Add clear filter handlers
    this.elements.toolbarInfo.querySelectorAll('[data-clear-filter]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const filterType = e.currentTarget.dataset.clearFilter;
        this.clearFilter(filterType);
      });
    });
  }
  
  /**
   * Clear a specific filter
   * @param {string} filterType - Type of filter to clear ('category' or 'search')
   */
  clearFilter(filterType) {
    if (filterType === 'category') {
      this.currentFilters.category = '';
      this.updateCategoryActiveState('');
    } else if (filterType === 'search') {
      this.currentFilters.search = '';
      this.elements.searchInput.value = '';
      this.toggleClearButton(false);
    }
    
    this.currentFilters.page = 1;
    this.performSearch();
  }
  
  /**
   * Show/hide loading overlay
   * @param {boolean} show - Whether to show loading
   */
  showLoading(show) {
    this.isLoading = show;
    
    if (this.elements.loadingOverlay) {
      this.elements.loadingOverlay.hidden = !show;
    }
    
    if (this.elements.productGrid) {
      this.elements.productGrid.style.opacity = show ? '0.5' : '1';
      this.elements.productGrid.style.pointerEvents = show ? 'none' : 'auto';
    }
  }
}

/**
 * Global App Class with CSRF Management
 * Handles authentication, API calls, notifications, and UI interactions
 * @class App
 * @example
 * // Access the global app instance
 * window.app.apiCall('/api/products/');
 * window.app.showSuccess('Item added to cart!');
 */
class App {
  /**
   * Create the App instance and initialize
   * @constructor
   */
  constructor() {
    /** @type {string|null} CSRF token for authenticated requests */
    this.csrftoken = this.getCookie('csrftoken');
    this.init();
  }

  /**
   * Retrieve a cookie value by name
   * @param {string} name - Cookie name to retrieve
   * @returns {string|null} Cookie value or null if not found
   * @private
   */
  getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  /**
   * Initialize the application
   * Sets up global events and prepares the app for use
   * @private
   */
  init() {
    this.setupGlobalEvents();
    // Cart initialization moved to Vite modules (cart.ts)
  }

  /**
   * Set up global DOM event listeners
   * Handles hamburger menu toggle and outside click detection
   * @private
   */
  setupGlobalEvents() {
    // Hamburger menu
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    if (hamburger) {
      hamburger.addEventListener('click', () => {
        navMenu?.classList.toggle('active');
        hamburger.classList.toggle('active');
      });
    }

    // Close mobile menu when clicking outside
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.nav-wrapper') && navMenu?.classList.contains('active')) {
        navMenu.classList.remove('active');
        hamburger?.classList.remove('active');
      }
    });
  }

  /**
   * Legacy cart initialization method
   * @deprecated Cart now initialized via Vite module (cart.ts)
   */
  initCart() {
    // Legacy method - cart now initialized via Vite module (cart.ts)
    // This method is kept for backward compatibility
  }

  /**
   * Make an authenticated API request
   * Automatically includes CSRF token and handles authentication errors
   * 
   * @async
   * @param {string} endpoint - API endpoint URL
   * @param {Object} [options={}] - Fetch API options
   * @param {string} [options.method='GET'] - HTTP method
   * @param {Object} [options.headers] - Additional headers
   * @param {Object|string} [options.body] - Request body
   * @returns {Promise<Object>} Parsed JSON response
   * @throws {Error} On authentication failure or network error
   * @example
   * // GET request
   * const data = await app.apiCall('/api/products/');
   * 
   * // POST request
   * const result = await app.apiCall('/api/cart/', {
   *   method: 'POST',
   *   body: JSON.stringify({ product_id: 123 })
   * });
   */
  async apiCall(endpoint, options = {}) {
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': this.csrftoken,
      },
      credentials: 'same-origin',
    };

    const mergedOptions = {
      ...defaultOptions,
      ...options,
      headers: {
        ...defaultOptions.headers,
        ...options.headers,
      },
    };

    try {
      const response = await fetch(endpoint, mergedOptions);
      
      if (response.status === 401 || response.status === 403) {
        if (response.status === 401) {
          window.location.href = '/accounts/login/?next=' + window.location.pathname;
        }
        throw new Error('Authentication required');
      }

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(error.detail || error.message || 'Request failed');
      }

      return await response.json();
    } catch (error) {
      console.error('API call failed:', error);
      this.showError(error.message);
      throw error;
    }
  }

  /**
   * Display an error notification
   * @param {string} message - Error message to display
   */
  showError(message) {
    this.showNotification(message, 'error');
  }

  /**
   * Display a success notification
   * @param {string} message - Success message to display
   */
  showSuccess(message) {
    this.showNotification(message, 'success');
  }

  /**
   * Display a notification toast message
   * Auto-dismisses after 3 seconds with slide animation
   * 
   * @param {string} message - Message text to display
   * @param {('info'|'success'|'error')} [type='info'] - Notification type
   */
  showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification--${type}`;
    notification.textContent = message;
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 1rem 1.5rem;
      background: ${type === 'error' ? 'var(--error-color)' : type === 'success' ? 'var(--success-color)' : 'var(--info-color)'};
      color: ${type === 'success' ? '#0b0b0b' : 'white'};
      border-radius: 8px;
      box-shadow: var(--shadow-lg);
      z-index: 10000;
      animation: slideIn 0.3s ease-out;
      max-width: 400px;
      font-weight: 600;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
      notification.style.animation = 'slideOut 0.3s ease-out';
      setTimeout(() => notification.remove(), 300);
    }, 3000);
  }

  /**
   * Toggle loading state on an element
   * Adds/removes 'loading' class and disables/enables element
   * 
   * @param {HTMLElement} element - Element to modify
   * @param {boolean} [show=true] - Whether to show loading state
   */
  showLoading(element, show = true) {
    if (show) {
      element.classList.add('loading');
      element.disabled = true;
    } else {
      element.classList.remove('loading');
      element.disabled = false;
    }
  }
}

/**
 * Initialize product detail page interactions
 * Sets up thumbnail image switching functionality
 * @function initProductDetailInteractions
 */
function initProductDetailInteractions() {
  const mainImage = document.getElementById('main-image');
  const productName = mainImage?.dataset.productName || '';

  document.querySelectorAll('[data-thumb-src]').forEach(thumb => {
    thumb.addEventListener('click', () => {
      const targetId = thumb.dataset.mainTarget;
      const target = targetId ? document.getElementById(targetId) : mainImage;
      const src = thumb.dataset.thumbSrc;
      if (!target || !src) return;
      target.innerHTML = `<img src="${src}" alt="${productName}" style="width: 100%; height: 100%; object-fit: contain;">`;
    });
  });
}

/**
 * Initialize hover raise effect on cards
 * Adds 'is-raised' class on mouseenter, removes on mouseleave
 * @function initHoverRaiseCards
 */
function initHoverRaiseCards() {
  document.querySelectorAll('[data-hover-raise]').forEach(card => {
    card.addEventListener('mouseenter', () => card.classList.add('is-raised'));
    card.addEventListener('mouseleave', () => card.classList.remove('is-raised'));
  });
}

// CSS injection removed per redesign request.

/**
 * Initialize products page view toggle (grid/list)
 * @function initViewToggle
 */
function initViewToggle() {
  const viewToggle = document.querySelector('.view-toggle');
  const productsGrid = document.querySelector('.products-grid');
  
  if (!viewToggle || !productsGrid) return;
  
  const buttons = viewToggle.querySelectorAll('.view-toggle__btn');
  
  // Load saved preference
  const savedView = localStorage.getItem('products-view') || 'grid';
  setView(savedView);
  
  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      const view = btn.dataset.view;
      setView(view);
      localStorage.setItem('products-view', view);
    });
  });
  
  function setView(view) {
    // Update buttons
    buttons.forEach(btn => {
      const isActive = btn.dataset.view === view;
      btn.classList.toggle('view-toggle__btn--active', isActive);
      btn.setAttribute('aria-pressed', isActive);
    });
    
    // Update grid
    productsGrid.classList.remove('products-grid--grid', 'products-grid--list');
    productsGrid.classList.add(`products-grid--${view}`);
    
    // Animate cards
    const cards = productsGrid.querySelectorAll('.product-card-v2');
    cards.forEach((card, i) => {
      card.style.opacity = '0';
      card.style.transform = 'translateY(20px)';
      setTimeout(() => {
        card.style.opacity = '1';
        card.style.transform = 'translateY(0)';
      }, i * 50);
    });
  }
}

/**
 * Initialize smooth page transitions
 * @function initPageTransitions
 */
function initPageTransitions() {
  // Add loaded class for initial animations
  document.body.classList.add('page-loaded');
  
  // Smooth scroll behavior
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      if (href === '#') return;
      
      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
}

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
    initProductDetailInteractions();
    initHoverRaiseCards();
    initViewToggle();
    initPageTransitions();
    initProductSearch();
  });
} else {
  window.app = new App();
  initProductDetailInteractions();
  initHoverRaiseCards();
  initViewToggle();
  initPageTransitions();
  initProductSearch();
}

/**
 * Initialize ProductSearch if on products page
 * @function initProductSearch
 */
function initProductSearch() {
  // Only initialize on products page
  if (!document.getElementById('products-search-input')) return;
  
  // Get config from page
  const config = window.PRODUCT_SEARCH_CONFIG || {};
  
  // Create ProductSearch instance
  window.productSearch = new ProductSearch(config);
}
