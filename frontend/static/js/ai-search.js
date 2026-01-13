/**
 * ============================================================================
 * PACKAXIS AI SEARCH - ENTERPRISE EDITION
 * ============================================================================
 * Version: 2.0.0
 * Last Updated: January 2026
 * 
 * Advanced AI-powered search with:
 * - Smart caching with TTL and LRU eviction
 * - Request prioritization and cancellation
 * - Exponential backoff retry logic
 * - Voice search support (Web Speech API)
 * - Analytics and telemetry integration
 * - Keyboard navigation with screen reader support
 * - Search history with sync support
 * - Trending searches integration
 * - Performance monitoring
 * - A/B testing support
 * - Cross-tab synchronization
 * 
 * WCAG 2.1 AA Compliant
 * ============================================================================
 */

(function(global, factory) {
  'use strict';
  
  if (typeof module === 'object' && typeof module.exports === 'object') {
    module.exports = factory();
  } else if (typeof define === 'function' && define.amd) {
    define(factory);
  } else {
    global.AISearch = factory();
  }
})(typeof window !== 'undefined' ? window : this, function() {
  'use strict';

  // ============================================================================
  // CONFIGURATION
  // ============================================================================
  
  const CONFIG = {
    // Search behavior
    MIN_CHARS: 2,
    MAX_CHARS: 200,
    DEBOUNCE_TIME: 250,
    MAX_RESULTS: 10,
    MAX_RECENT_SEARCHES: 15,
    MAX_TRENDING_SEARCHES: 5,
    
    // Cache settings
    CACHE_MAX_SIZE: 100,
    CACHE_TTL: 5 * 60 * 1000, // 5 minutes
    CACHE_STALE_TTL: 30 * 60 * 1000, // 30 minutes (stale-while-revalidate)
    
    // Network settings
    REQUEST_TIMEOUT: 8000,
    MAX_RETRIES: 3,
    RETRY_BASE_DELAY: 1000,
    RETRY_MAX_DELAY: 10000,
    
    // Storage keys
    STORAGE_KEY_RECENT: 'packaxis_search_recent',
    STORAGE_KEY_PREFS: 'packaxis_search_prefs',
    STORAGE_KEY_ANALYTICS: 'packaxis_search_analytics',
    
    // Voice search
    VOICE_ENABLED: true,
    VOICE_LANG: 'en-CA',
    VOICE_CONTINUOUS: false,
    
    // API endpoints
    API_ENDPOINT: '/api/products/autocomplete/',
    TRENDING_ENDPOINT: '/api/products/trending/',
    ANALYTICS_ENDPOINT: '/api/analytics/search/',
    
    // Feature flags
    FEATURES: {
      voiceSearch: true,
      trendingSearches: true,
      searchHistory: true,
      analytics: true,
      instantResults: true,
      highlightMatches: true,
      keyboardNavigation: true,
      crossTabSync: true,
      showCategories: true
    }
  };

  // ============================================================================
  // UTILITY FUNCTIONS
  // ============================================================================
  
  const Utils = {
    /**
     * Generate unique ID
     */
    generateId() {
      return `search_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    },

    /**
     * Debounce function with leading/trailing options
     */
    debounce(fn, delay, options = {}) {
      let timeoutId = null;
      let lastArgs = null;
      const { leading = false, trailing = true } = options;

      const debounced = function(...args) {
        lastArgs = args;
        const shouldCallNow = leading && !timeoutId;

        clearTimeout(timeoutId);

        timeoutId = setTimeout(() => {
          timeoutId = null;
          if (trailing && lastArgs) {
            fn.apply(this, lastArgs);
          }
        }, delay);

        if (shouldCallNow) {
          fn.apply(this, args);
        }
      };

      debounced.cancel = () => {
        clearTimeout(timeoutId);
        timeoutId = null;
        lastArgs = null;
      };

      debounced.flush = () => {
        if (timeoutId && lastArgs) {
          fn.apply(this, lastArgs);
          clearTimeout(timeoutId);
          timeoutId = null;
          lastArgs = null;
        }
      };

      return debounced;
    },

    /**
     * Throttle function
     */
    throttle(fn, limit) {
      let inThrottle = false;
      return function(...args) {
        if (!inThrottle) {
          fn.apply(this, args);
          inThrottle = true;
          setTimeout(() => inThrottle = false, limit);
        }
      };
    },

    /**
     * Escape HTML entities
     */
    escapeHtml(text) {
      if (!text) return '';
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
    },

    /**
     * Escape regex special characters
     */
    escapeRegex(text) {
      return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    },

    /**
     * Highlight matching text
     */
    highlightText(text, query) {
      if (!query || !text) return Utils.escapeHtml(text);
      const escaped = Utils.escapeHtml(text);
      const regex = new RegExp(`(${Utils.escapeRegex(query)})`, 'gi');
      return escaped.replace(regex, '<mark class="ai-search-highlight">$1</mark>');
    },

    /**
     * Format price
     */
    formatPrice(price, currency = 'CAD') {
      const num = parseFloat(price);
      if (isNaN(num)) return '';
      return new Intl.NumberFormat('en-CA', {
        style: 'currency',
        currency
      }).format(num);
    },

    /**
     * Calculate string similarity (Levenshtein-based)
     */
    similarity(str1, str2) {
      const s1 = str1.toLowerCase();
      const s2 = str2.toLowerCase();
      if (s1 === s2) return 1;
      
      const len1 = s1.length;
      const len2 = s2.length;
      const matrix = [];

      for (let i = 0; i <= len1; i++) {
        matrix[i] = [i];
      }
      for (let j = 0; j <= len2; j++) {
        matrix[0][j] = j;
      }

      for (let i = 1; i <= len1; i++) {
        for (let j = 1; j <= len2; j++) {
          const cost = s1[i - 1] === s2[j - 1] ? 0 : 1;
          matrix[i][j] = Math.min(
            matrix[i - 1][j] + 1,
            matrix[i][j - 1] + 1,
            matrix[i - 1][j - 1] + cost
          );
        }
      }

      const distance = matrix[len1][len2];
      return 1 - distance / Math.max(len1, len2);
    },

    /**
     * Deep merge objects
     */
    deepMerge(target, ...sources) {
      if (!sources.length) return target;
      const source = sources.shift();

      if (typeof target === 'object' && typeof source === 'object') {
        for (const key in source) {
          if (Object.prototype.hasOwnProperty.call(source, key)) {
            if (typeof source[key] === 'object' && source[key] !== null && !Array.isArray(source[key])) {
              if (!target[key]) Object.assign(target, { [key]: {} });
              Utils.deepMerge(target[key], source[key]);
            } else {
              Object.assign(target, { [key]: source[key] });
            }
          }
        }
      }

      return Utils.deepMerge(target, ...sources);
    }
  };

  // ============================================================================
  // LRU CACHE WITH TTL
  // ============================================================================
  
  class LRUCache {
    constructor(maxSize = CONFIG.CACHE_MAX_SIZE, ttl = CONFIG.CACHE_TTL) {
      this.maxSize = maxSize;
      this.ttl = ttl;
      this.cache = new Map();
      this.timestamps = new Map();
    }

    get(key) {
      if (!this.cache.has(key)) return null;

      const timestamp = this.timestamps.get(key);
      const now = Date.now();
      const age = now - timestamp;

      // Check if expired
      if (age > this.ttl) {
        // Return stale data with flag if within stale TTL
        if (age <= CONFIG.CACHE_STALE_TTL) {
          return { data: this.cache.get(key), stale: true };
        }
        this.delete(key);
        return null;
      }

      // Move to end (most recently used)
      const value = this.cache.get(key);
      this.cache.delete(key);
      this.cache.set(key, value);

      return { data: value, stale: false };
    }

    set(key, value) {
      // Delete if exists (to update position)
      if (this.cache.has(key)) {
        this.cache.delete(key);
      }

      // Evict oldest if at capacity
      if (this.cache.size >= this.maxSize) {
        const oldestKey = this.cache.keys().next().value;
        this.delete(oldestKey);
      }

      this.cache.set(key, value);
      this.timestamps.set(key, Date.now());
    }

    delete(key) {
      this.cache.delete(key);
      this.timestamps.delete(key);
    }

    clear() {
      this.cache.clear();
      this.timestamps.clear();
    }

    has(key) {
      if (!this.cache.has(key)) return false;
      const timestamp = this.timestamps.get(key);
      return (Date.now() - timestamp) <= this.ttl;
    }

    size() {
      return this.cache.size;
    }

    getStats() {
      return {
        size: this.cache.size,
        maxSize: this.maxSize,
        ttl: this.ttl
      };
    }
  }

  // ============================================================================
  // REQUEST MANAGER (Prioritization & Cancellation)
  // ============================================================================
  
  class RequestManager {
    constructor() {
      this.pendingRequests = new Map();
      this.abortControllers = new Map();
    }

    /**
     * Create a cancellable request
     */
    async fetch(url, options = {}, priority = 'normal') {
      const requestId = options.requestId || Utils.generateId();

      // Cancel any existing request for same query
      if (options.cancelPrevious && this.abortControllers.has(options.cancelKey)) {
        this.abort(options.cancelKey);
      }

      const controller = new AbortController();
      this.abortControllers.set(options.cancelKey || requestId, controller);

      const timeoutId = setTimeout(() => {
        controller.abort();
      }, options.timeout || CONFIG.REQUEST_TIMEOUT);

      try {
        const response = await fetch(url, {
          ...options,
          signal: controller.signal,
          headers: {
            'Content-Type': 'application/json',
            'X-Request-Priority': priority,
            'X-Request-ID': requestId,
            ...options.headers
          }
        });

        clearTimeout(timeoutId);
        this.abortControllers.delete(options.cancelKey || requestId);

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
      } catch (error) {
        clearTimeout(timeoutId);
        this.abortControllers.delete(options.cancelKey || requestId);

        if (error.name === 'AbortError') {
          throw new Error('Request cancelled');
        }
        throw error;
      }
    }

    /**
     * Abort a specific request
     */
    abort(key) {
      const controller = this.abortControllers.get(key);
      if (controller) {
        controller.abort();
        this.abortControllers.delete(key);
      }
    }

    /**
     * Abort all pending requests
     */
    abortAll() {
      this.abortControllers.forEach(controller => controller.abort());
      this.abortControllers.clear();
    }

    /**
     * Retry with exponential backoff
     */
    async fetchWithRetry(url, options = {}, maxRetries = CONFIG.MAX_RETRIES) {
      let lastError;
      let delay = CONFIG.RETRY_BASE_DELAY;

      for (let attempt = 0; attempt <= maxRetries; attempt++) {
        try {
          return await this.fetch(url, options);
        } catch (error) {
          lastError = error;

          // Don't retry on cancellation or client errors
          if (error.message === 'Request cancelled' || 
              error.message.includes('HTTP 4')) {
            throw error;
          }

          if (attempt < maxRetries) {
            // Exponential backoff with jitter
            const jitter = Math.random() * 0.3 * delay;
            await new Promise(resolve => setTimeout(resolve, delay + jitter));
            delay = Math.min(delay * 2, CONFIG.RETRY_MAX_DELAY);
          }
        }
      }

      throw lastError;
    }
  }

  // ============================================================================
  // ANALYTICS TRACKER
  // ============================================================================
  
  class AnalyticsTracker {
    constructor(options = {}) {
      this.enabled = options.enabled !== false && CONFIG.FEATURES.analytics;
      this.endpoint = options.endpoint || CONFIG.ANALYTICS_ENDPOINT;
      this.buffer = [];
      this.sessionId = Utils.generateId();
      this.flushInterval = null;

      if (this.enabled) {
        this.startFlushInterval();
      }
    }

    track(eventType, data) {
      if (!this.enabled) return;

      const event = {
        type: eventType,
        timestamp: Date.now(),
        sessionId: this.sessionId,
        url: window.location.href,
        ...data
      };

      this.buffer.push(event);

      // Immediate flush for critical events
      if (['search_submit', 'product_click'].includes(eventType)) {
        this.flush();
      }
    }

    trackSearch(query, resultsCount, responseTime) {
      this.track('search', {
        query,
        resultsCount,
        responseTime,
        queryLength: query.length
      });
    }

    trackClick(type, id, query, position) {
      this.track('click', {
        itemType: type,
        itemId: id,
        query,
        position
      });
    }

    trackVoiceSearch(query, success) {
      this.track('voice_search', {
        query,
        success
      });
    }

    trackError(error, context) {
      this.track('error', {
        error: error.message,
        context
      });
    }

    startFlushInterval() {
      this.flushInterval = setInterval(() => this.flush(), 30000);
    }

    async flush() {
      if (this.buffer.length === 0) return;

      const events = [...this.buffer];
      this.buffer = [];

      try {
        // Use sendBeacon for reliability
        if (navigator.sendBeacon) {
          navigator.sendBeacon(
            this.endpoint,
            JSON.stringify({ events })
          );
        } else {
          await fetch(this.endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ events }),
            keepalive: true
          });
        }
      } catch (error) {
        // Re-add events on failure
        this.buffer = events.concat(this.buffer);
        console.warn('Analytics flush failed:', error);
      }
    }

    destroy() {
      this.flush();
      if (this.flushInterval) {
        clearInterval(this.flushInterval);
      }
    }
  }

  // ============================================================================
  // VOICE SEARCH
  // ============================================================================
  
  class VoiceSearch {
    constructor(options = {}) {
      this.enabled = options.enabled !== false && CONFIG.FEATURES.voiceSearch;
      this.lang = options.lang || CONFIG.VOICE_LANG;
      this.continuous = options.continuous || CONFIG.VOICE_CONTINUOUS;
      this.recognition = null;
      this.isListening = false;
      this.onResult = options.onResult || (() => {});
      this.onError = options.onError || (() => {});
      this.onStateChange = options.onStateChange || (() => {});

      if (this.enabled && this.isSupported()) {
        this.init();
      }
    }

    isSupported() {
      return 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
    }

    init() {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      this.recognition = new SpeechRecognition();
      this.recognition.lang = this.lang;
      this.recognition.continuous = this.continuous;
      this.recognition.interimResults = true;
      this.recognition.maxAlternatives = 3;

      this.recognition.onresult = (event) => {
        const results = event.results;
        const lastResult = results[results.length - 1];
        
        if (lastResult.isFinal) {
          const transcript = lastResult[0].transcript.trim();
          this.onResult(transcript, lastResult[0].confidence);
        } else {
          // Interim result
          const interim = lastResult[0].transcript.trim();
          this.onResult(interim, lastResult[0].confidence, true);
        }
      };

      this.recognition.onerror = (event) => {
        this.isListening = false;
        this.onStateChange('error', event.error);
        this.onError(event.error);
      };

      this.recognition.onend = () => {
        this.isListening = false;
        this.onStateChange('ended');
      };

      this.recognition.onstart = () => {
        this.isListening = true;
        this.onStateChange('listening');
      };
    }

    start() {
      if (!this.recognition || this.isListening) return false;
      
      try {
        this.recognition.start();
        return true;
      } catch (error) {
        console.error('Voice search start failed:', error);
        return false;
      }
    }

    stop() {
      if (!this.recognition || !this.isListening) return;
      this.recognition.stop();
    }

    abort() {
      if (!this.recognition) return;
      this.recognition.abort();
      this.isListening = false;
    }

    getState() {
      return {
        enabled: this.enabled,
        supported: this.isSupported(),
        listening: this.isListening
      };
    }
  }

  // ============================================================================
  // SEARCH HISTORY MANAGER
  // ============================================================================
  
  class SearchHistory {
    constructor(options = {}) {
      this.storageKey = options.storageKey || CONFIG.STORAGE_KEY_RECENT;
      this.maxItems = options.maxItems || CONFIG.MAX_RECENT_SEARCHES;
      this.syncEnabled = options.syncEnabled !== false && CONFIG.FEATURES.crossTabSync;
      this.items = this.load();

      if (this.syncEnabled) {
        this.setupCrossTabSync();
      }
    }

    load() {
      try {
        const data = localStorage.getItem(this.storageKey);
        if (!data) return [];
        
        const parsed = JSON.parse(data);
        // Validate and clean data
        return parsed
          .filter(item => item && typeof item.query === 'string')
          .slice(0, this.maxItems);
      } catch (error) {
        console.warn('Failed to load search history:', error);
        return [];
      }
    }

    save() {
      try {
        localStorage.setItem(this.storageKey, JSON.stringify(this.items));
      } catch (error) {
        console.warn('Failed to save search history:', error);
      }
    }

    add(query, metadata = {}) {
      if (!query || typeof query !== 'string' || query.length < CONFIG.MIN_CHARS) {
        return;
      }

      const normalizedQuery = query.trim().toLowerCase();
      
      // Remove existing entry
      this.items = this.items.filter(
        item => item.query.toLowerCase() !== normalizedQuery
      );

      // Add to front
      this.items.unshift({
        query: query.trim(),
        timestamp: Date.now(),
        ...metadata
      });

      // Trim to max
      this.items = this.items.slice(0, this.maxItems);
      this.save();
    }

    remove(query) {
      const normalizedQuery = query.toLowerCase();
      this.items = this.items.filter(
        item => item.query.toLowerCase() !== normalizedQuery
      );
      this.save();
    }

    clear() {
      this.items = [];
      this.save();
    }

    getRecent(limit = 5) {
      return this.items.slice(0, limit);
    }

    search(query) {
      if (!query) return this.getRecent();
      
      const normalizedQuery = query.toLowerCase();
      return this.items.filter(
        item => item.query.toLowerCase().includes(normalizedQuery)
      );
    }

    setupCrossTabSync() {
      window.addEventListener('storage', (event) => {
        if (event.key === this.storageKey) {
          this.items = this.load();
        }
      });
    }
  }

  // ============================================================================
  // MAIN AI SEARCH CLASS
  // ============================================================================
  
  class AISearch {
    constructor(inputElement, options = {}) {
      if (!inputElement || !(inputElement instanceof HTMLElement)) {
        throw new Error('AISearch: Valid input element required');
      }

      this.id = Utils.generateId();
      this.input = inputElement;
      this.options = Utils.deepMerge({}, CONFIG, options);
      
      // Core components
      this.cache = new LRUCache(
        this.options.CACHE_MAX_SIZE,
        this.options.CACHE_TTL
      );
      this.requestManager = new RequestManager();
      this.analytics = new AnalyticsTracker({
        enabled: this.options.FEATURES.analytics,
        endpoint: this.options.ANALYTICS_ENDPOINT
      });
      this.history = new SearchHistory({
        storageKey: this.options.STORAGE_KEY_RECENT,
        maxItems: this.options.MAX_RECENT_SEARCHES
      });
      this.voiceSearch = new VoiceSearch({
        enabled: this.options.FEATURES.voiceSearch,
        onResult: this.handleVoiceResult.bind(this),
        onError: this.handleVoiceError.bind(this),
        onStateChange: this.handleVoiceStateChange.bind(this)
      });

      // State
      this.state = {
        isOpen: false,
        isLoading: false,
        currentQuery: '',
        focusIndex: -1,
        results: null,
        error: null,
        voiceListening: false
      };

      // DOM references
      this.container = null;
      this.resultsContainer = null;
      this.voiceButton = null;

      // Callbacks
      this.onSelect = options.onSelect || this.defaultOnSelect.bind(this);
      this.onSearch = options.onSearch || null;

      // Debounced search
      this.debouncedSearch = Utils.debounce(
        this.executeSearch.bind(this),
        this.options.DEBOUNCE_TIME
      );

      // Performance tracking
      this.metrics = {
        searchCount: 0,
        cacheHits: 0,
        cacheMisses: 0,
        avgResponseTime: 0
      };

      this.init();
    }

    // ========================================================================
    // INITIALIZATION
    // ========================================================================

    init() {
      this.createDOM();
      this.bindEvents();
      this.setupAccessibility();
      this.loadTrendingSearches();
    }

    createDOM() {
      // Wrap input if not already wrapped
      const wrapper = this.input.closest('.ai-search-wrapper') || this.input.closest('.nav-search-wrapper') || this.createWrapper();
      this.container = wrapper;
      wrapper.classList.add('ai-search-wrapper');

      // Create results container
      this.resultsContainer = document.createElement('div');
      this.resultsContainer.className = 'ai-search-dropdown';
      this.resultsContainer.id = `${this.id}-results`;
      this.resultsContainer.setAttribute('role', 'listbox');
      this.resultsContainer.setAttribute('aria-label', 'Search suggestions');
      this.resultsContainer.hidden = true;
      wrapper.appendChild(this.resultsContainer);

      // Create voice search button if enabled
      if (this.options.FEATURES.voiceSearch && this.voiceSearch.isSupported()) {
        this.voiceButton = document.createElement('button');
        this.voiceButton.type = 'button';
        this.voiceButton.className = 'ai-search-voice-btn';
        this.voiceButton.setAttribute('aria-label', 'Search by voice');
        this.voiceButton.innerHTML = `
          <span class="material-symbols-rounded" aria-hidden="true">mic</span>
        `;
        
        const inputWrapper = this.input.parentElement;
        if (inputWrapper.classList.contains('nav-search-input-wrapper')) {
          inputWrapper.appendChild(this.voiceButton);
        }
      }

      // Add loading indicator
      this.loadingIndicator = document.createElement('div');
      this.loadingIndicator.className = 'ai-search-loading-indicator';
      this.loadingIndicator.hidden = true;
      this.loadingIndicator.innerHTML = `
        <div class="ai-search-spinner" aria-hidden="true"></div>
      `;
      wrapper.appendChild(this.loadingIndicator);
    }

    createWrapper() {
      const wrapper = document.createElement('div');
      wrapper.className = 'ai-search-wrapper';
      this.input.parentNode.insertBefore(wrapper, this.input);
      
      // Move input into wrapper
      const inputParent = this.input.parentElement;
      if (inputParent !== wrapper) {
        wrapper.appendChild(inputParent.contains(this.input) ? this.input : inputParent);
      }
      
      return wrapper;
    }

    setupAccessibility() {
      // Input ARIA attributes
      this.input.setAttribute('role', 'combobox');
      this.input.setAttribute('aria-autocomplete', 'list');
      this.input.setAttribute('aria-expanded', 'false');
      this.input.setAttribute('aria-controls', this.resultsContainer.id);
      this.input.setAttribute('aria-haspopup', 'listbox');
      this.input.setAttribute('autocomplete', 'off');
      this.input.setAttribute('autocapitalize', 'off');
      this.input.setAttribute('autocorrect', 'off');
      this.input.setAttribute('spellcheck', 'false');
      
      // Live region for screen readers
      this.liveRegion = document.createElement('div');
      this.liveRegion.setAttribute('role', 'status');
      this.liveRegion.setAttribute('aria-live', 'polite');
      this.liveRegion.setAttribute('aria-atomic', 'true');
      this.liveRegion.className = 'sr-only';
      this.container.appendChild(this.liveRegion);
    }

    // ========================================================================
    // EVENT BINDING
    // ========================================================================

    bindEvents() {
      // Input events
      this.input.addEventListener('input', this.handleInput.bind(this));
      this.input.addEventListener('focus', this.handleFocus.bind(this));
      this.input.addEventListener('blur', this.handleBlur.bind(this));
      this.input.addEventListener('keydown', this.handleKeyDown.bind(this));

      // Form submission
      const form = this.input.closest('form');
      if (form) {
        form.addEventListener('submit', this.handleFormSubmit.bind(this));
      }

      // Results container events (event delegation)
      this.resultsContainer.addEventListener('click', this.handleResultClick.bind(this));
      this.resultsContainer.addEventListener('mouseenter', this.handleResultHover.bind(this), true);

      // Voice button
      if (this.voiceButton) {
        this.voiceButton.addEventListener('click', this.handleVoiceButtonClick.bind(this));
      }

      // Click outside to close
      document.addEventListener('click', this.handleClickOutside.bind(this));

      // Escape key at document level
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && this.state.isOpen) {
          this.close();
          this.input.focus();
        }
      });

      // Cross-tab sync
      if (this.options.FEATURES.crossTabSync) {
        window.addEventListener('storage', this.handleStorageChange.bind(this));
      }

      // Visibility change (pause/resume)
      document.addEventListener('visibilitychange', () => {
        if (document.hidden && this.state.isLoading) {
          this.requestManager.abortAll();
        }
      });
    }

    // ========================================================================
    // EVENT HANDLERS
    // ========================================================================

    handleInput(event) {
      const query = event.target.value.trim();
      this.state.currentQuery = query;

      if (query.length < this.options.MIN_CHARS) {
        if (this.options.FEATURES.searchHistory && this.history.items.length > 0) {
          this.showRecentSearches();
        } else {
          this.close();
        }
        return;
      }

      if (query.length > this.options.MAX_CHARS) {
        return;
      }

      this.showLoading();
      this.debouncedSearch(query);
    }

    handleFocus() {
      const query = this.input.value.trim();
      
      if (query.length >= this.options.MIN_CHARS) {
        // Check cache first
        const cached = this.cache.get(query);
        if (cached) {
          this.renderResults(cached.data, query);
        } else {
          this.executeSearch(query);
        }
      } else if (this.options.FEATURES.searchHistory) {
        this.showRecentSearches();
      }
    }

    handleBlur() {
      // Delay to allow click on results
      setTimeout(() => {
        if (!this.resultsContainer.matches(':hover') && 
            !this.resultsContainer.contains(document.activeElement)) {
          this.close();
        }
      }, 200);
    }

    handleKeyDown(event) {
      const { key } = event;
      const items = this.resultsContainer.querySelectorAll('.ai-search-item[role="option"]');
      const itemCount = items.length;

      switch (key) {
        case 'ArrowDown':
          event.preventDefault();
          if (!this.state.isOpen && this.state.currentQuery) {
            this.executeSearch(this.state.currentQuery);
          } else {
            this.state.focusIndex = Math.min(this.state.focusIndex + 1, itemCount - 1);
            this.updateFocus(items);
          }
          break;

        case 'ArrowUp':
          event.preventDefault();
          this.state.focusIndex = Math.max(this.state.focusIndex - 1, -1);
          this.updateFocus(items);
          break;

        case 'Enter':
          event.preventDefault();
          if (this.state.focusIndex >= 0 && items[this.state.focusIndex]) {
            this.selectItem(items[this.state.focusIndex]);
          } else if (this.state.currentQuery) {
            this.performSearch(this.state.currentQuery);
          }
          break;

        case 'Tab':
          if (this.state.isOpen) {
            this.close();
          }
          break;

        case 'Home':
          if (this.state.isOpen && itemCount > 0) {
            event.preventDefault();
            this.state.focusIndex = 0;
            this.updateFocus(items);
          }
          break;

        case 'End':
          if (this.state.isOpen && itemCount > 0) {
            event.preventDefault();
            this.state.focusIndex = itemCount - 1;
            this.updateFocus(items);
          }
          break;
      }
    }

    handleFormSubmit(event) {
      if (this.state.isOpen && this.state.focusIndex >= 0) {
        event.preventDefault();
        const items = this.resultsContainer.querySelectorAll('.ai-search-item[role="option"]');
        if (items[this.state.focusIndex]) {
          this.selectItem(items[this.state.focusIndex]);
        }
      }
    }

    handleResultClick(event) {
      const item = event.target.closest('.ai-search-item');
      const removeBtn = event.target.closest('.ai-search-remove-btn');
      const clearAllBtn = event.target.closest('.ai-search-clear-all');

      if (removeBtn) {
        event.preventDefault();
        event.stopPropagation();
        const query = removeBtn.dataset.query;
        this.history.remove(query);
        this.showRecentSearches();
        return;
      }

      if (clearAllBtn) {
        event.preventDefault();
        this.history.clear();
        this.close();
        return;
      }

      if (item) {
        event.preventDefault();
        this.selectItem(item);
      }
    }

    handleResultHover(event) {
      const item = event.target.closest('.ai-search-item');
      if (item) {
        const items = this.resultsContainer.querySelectorAll('.ai-search-item[role="option"]');
        this.state.focusIndex = Array.from(items).indexOf(item);
        this.updateFocus(items);
      }
    }

    handleClickOutside(event) {
      if (!this.container.contains(event.target)) {
        this.close();
      }
    }

    handleStorageChange(event) {
      if (event.key === this.options.STORAGE_KEY_RECENT) {
        this.history.items = this.history.load();
      }
    }

    handleVoiceButtonClick(event) {
      event.preventDefault();
      
      if (this.state.voiceListening) {
        this.voiceSearch.stop();
      } else {
        this.voiceSearch.start();
      }
    }

    handleVoiceResult(transcript, confidence, isInterim = false) {
      this.input.value = transcript;
      this.state.currentQuery = transcript;

      if (!isInterim) {
        this.analytics.trackVoiceSearch(transcript, true);
        this.executeSearch(transcript);
      }
    }

    handleVoiceError(error) {
      this.analytics.trackVoiceSearch('', false);
      this.announce(`Voice search error: ${error}`);
    }

    handleVoiceStateChange(state) {
      this.state.voiceListening = state === 'listening';
      
      if (this.voiceButton) {
        this.voiceButton.classList.toggle('listening', this.state.voiceListening);
        this.voiceButton.setAttribute(
          'aria-label',
          this.state.voiceListening ? 'Stop voice search' : 'Search by voice'
        );
        
        // Update icon
        const icon = this.voiceButton.querySelector('.material-symbols-rounded');
        if (icon) {
          icon.textContent = this.state.voiceListening ? 'mic_off' : 'mic';
        }
      }
    }

    // ========================================================================
    // SEARCH EXECUTION
    // ========================================================================

    async executeSearch(query) {
      if (!query || query.length < this.options.MIN_CHARS) {
        return;
      }

      const startTime = performance.now();
      this.state.isLoading = true;
      this.state.error = null;

      // Check cache
      const cached = this.cache.get(query);
      if (cached && !cached.stale) {
        this.metrics.cacheHits++;
        this.renderResults(cached.data, query);
        this.state.isLoading = false;
        return;
      }

      // Show stale data while revalidating
      if (cached && cached.stale) {
        this.renderResults(cached.data, query);
      }

      this.metrics.cacheMisses++;

      try {
        const url = `${this.options.API_ENDPOINT}?q=${encodeURIComponent(query)}&max=${this.options.MAX_RESULTS}`;
        
        const data = await this.requestManager.fetchWithRetry(url, {
          cancelPrevious: true,
          cancelKey: 'search',
          timeout: this.options.REQUEST_TIMEOUT
        });

        // Cache results
        this.cache.set(query, data);

        // Track metrics
        const responseTime = performance.now() - startTime;
        this.metrics.searchCount++;
        this.metrics.avgResponseTime = 
          (this.metrics.avgResponseTime * (this.metrics.searchCount - 1) + responseTime) / 
          this.metrics.searchCount;

        // Track analytics
        this.analytics.trackSearch(
          query,
          (data.products?.length || 0) + (data.categories?.length || 0),
          responseTime
        );

        this.renderResults(data, query);
      } catch (error) {
        if (error.message !== 'Request cancelled') {
          this.state.error = error;
          this.analytics.trackError(error, 'search');
          this.showError('Unable to load results. Please try again.');
        }
      } finally {
        this.state.isLoading = false;
        this.loadingIndicator.hidden = true;
      }
    }

    async loadTrendingSearches() {
      if (!this.options.FEATURES.trendingSearches) return;

      try {
        const response = await fetch(this.options.TRENDING_ENDPOINT);
        if (response.ok) {
          const data = await response.json();
          this.trendingSearches = data.trending || [];
        }
      } catch (error) {
        // Silently fail - trending is optional
      }
    }

    // ========================================================================
    // RENDERING
    // ========================================================================

    renderResults(data, query) {
      this.state.focusIndex = -1;
      
      const sections = [];

      // Products section
      if (data.products && data.products.length > 0) {
        sections.push(this.renderProductsSection(data.products, query));
      }

      // Categories section
      if (this.options.FEATURES.showCategories && data.categories?.length > 0) {
        sections.push(this.renderCategoriesSection(data.categories));
      }

      // AI Suggestions section
      if (data.suggestions && data.suggestions.length > 0) {
        sections.push(this.renderSuggestionsSection(data.suggestions));
      }

      // No results state
      if (sections.length === 0) {
        this.resultsContainer.innerHTML = this.renderNoResults(query);
        this.open();
        this.announce(`No results found for ${query}`);
        return;
      }

      // Footer with view all
      let footer = '';
      if (data.total_count > this.options.MAX_RESULTS) {
        footer = this.renderFooter(query, data.total_count);
      }

      this.resultsContainer.innerHTML = sections.join('') + footer;
      this.open();

      // Announce results count
      const totalResults = (data.products?.length || 0) + (data.categories?.length || 0);
      this.announce(`${totalResults} suggestions available. Use arrow keys to navigate.`);
    }

    renderProductsSection(products, query) {
      const items = products.map((product, index) => 
        this.renderProductItem(product, query, index)
      ).join('');

      return `
        <div class="ai-search-section" role="group" aria-label="Products">
          <div class="ai-search-section-header">
            <span class="material-symbols-rounded" aria-hidden="true">inventory_2</span>
            <span class="ai-search-section-title">Products</span>
          </div>
          <div class="ai-search-section-content">
            ${items}
          </div>
        </div>
      `;
    }

    renderProductItem(product, query, index) {
      const highlighted = Utils.highlightText(product.name, query);
      const price = product.price ? Utils.formatPrice(product.price) : '';
      const stockStatus = product.in_stock !== false;
      const stockBadge = stockStatus 
        ? '<span class="ai-search-badge ai-search-badge--success">In Stock</span>'
        : '<span class="ai-search-badge ai-search-badge--danger">Out of Stock</span>';

      const placeholderSvg = `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='60' height='60' viewBox='0 0 24 24' fill='none' stroke='%23bdbdbd' stroke-width='1.5'%3E%3Crect x='3' y='3' width='18' height='18' rx='2'/%3E%3Ccircle cx='8.5' cy='8.5' r='1.5'/%3E%3Cpolyline points='21 15 16 10 5 21'/%3E%3C/svg%3E`;
      const imageUrl = product.image_url || product.thumbnail || placeholderSvg;

      return `
        <div class="ai-search-item ai-search-item--product" 
             role="option" 
             id="${this.id}-item-${index}"
             aria-selected="false"
             data-type="product"
             data-id="${product.id}"
             data-url="${Utils.escapeHtml(product.url)}"
             data-position="${index}"
             tabindex="-1">
          <div class="ai-search-item__image">
            <img src="${imageUrl}" 
                 alt="" 
                 loading="lazy" 
                 onerror="this.src='${placeholderSvg}'">
          </div>
          <div class="ai-search-item__content">
            <div class="ai-search-item__title">${highlighted}</div>
            ${product.category ? `<div class="ai-search-item__meta">${Utils.escapeHtml(product.category)}</div>` : ''}
            <div class="ai-search-item__footer">
              ${price ? `<span class="ai-search-item__price">${price}</span>` : ''}
              ${stockBadge}
            </div>
          </div>
          <span class="material-symbols-rounded ai-search-item__arrow" aria-hidden="true">chevron_right</span>
        </div>
      `;
    }

    renderCategoriesSection(categories) {
      const items = categories.map((category, index) => `
        <div class="ai-search-item ai-search-item--category" 
             role="option"
             id="${this.id}-cat-${index}"
             aria-selected="false"
             data-type="category"
             data-id="${category.id}"
             data-url="${Utils.escapeHtml(category.url)}"
             tabindex="-1">
          <span class="material-symbols-rounded ai-search-item__icon" aria-hidden="true">category</span>
          <div class="ai-search-item__content">
            <div class="ai-search-item__title">${Utils.escapeHtml(category.name)}</div>
            ${category.product_count ? `<div class="ai-search-item__meta">${category.product_count} products</div>` : ''}
          </div>
          <span class="material-symbols-rounded ai-search-item__arrow" aria-hidden="true">chevron_right</span>
        </div>
      `).join('');

      return `
        <div class="ai-search-section" role="group" aria-label="Categories">
          <div class="ai-search-section-header">
            <span class="material-symbols-rounded" aria-hidden="true">category</span>
            <span class="ai-search-section-title">Categories</span>
          </div>
          <div class="ai-search-section-content">
            ${items}
          </div>
        </div>
      `;
    }

    renderSuggestionsSection(suggestions) {
      const items = suggestions.map((suggestion, index) => `
        <div class="ai-search-item ai-search-item--suggestion" 
             role="option"
             id="${this.id}-sug-${index}"
             aria-selected="false"
             data-type="suggestion"
             data-query="${Utils.escapeHtml(suggestion.text)}"
             tabindex="-1">
          <span class="material-symbols-rounded ai-search-item__icon" aria-hidden="true">auto_awesome</span>
          <div class="ai-search-item__content">
            <div class="ai-search-item__title">${Utils.escapeHtml(suggestion.text)}</div>
            ${suggestion.reason ? `<div class="ai-search-item__meta">${Utils.escapeHtml(suggestion.reason)}</div>` : ''}
          </div>
        </div>
      `).join('');

      return `
        <div class="ai-search-section" role="group" aria-label="AI Suggestions">
          <div class="ai-search-section-header">
            <span class="material-symbols-rounded" aria-hidden="true">psychology</span>
            <span class="ai-search-section-title">AI Suggestions</span>
          </div>
          <div class="ai-search-section-content">
            ${items}
          </div>
        </div>
      `;
    }

    renderNoResults(query) {
      return `
        <div class="ai-search-empty" role="status">
          <span class="material-symbols-rounded ai-search-empty__icon" aria-hidden="true">search_off</span>
          <p class="ai-search-empty__title">No results found</p>
          <p class="ai-search-empty__message">No matches for "${Utils.escapeHtml(query)}"</p>
          <p class="ai-search-empty__hint">Try different keywords or check spelling</p>
        </div>
      `;
    }

    renderFooter(query, totalCount) {
      return `
        <div class="ai-search-footer">
          <a href="/products/?q=${encodeURIComponent(query)}" 
             class="ai-search-view-all"
             data-type="view-all">
            View all ${totalCount} results
            <span class="material-symbols-rounded" aria-hidden="true">arrow_forward</span>
          </a>
        </div>
      `;
    }

    showRecentSearches() {
      const recentItems = this.history.getRecent(5);
      
      if (recentItems.length === 0) {
        if (this.trendingSearches?.length > 0) {
          this.showTrendingSearches();
        } else {
          this.close();
        }
        return;
      }

      const items = recentItems.map((item, index) => `
        <div class="ai-search-item ai-search-item--recent" 
             role="option"
             id="${this.id}-recent-${index}"
             aria-selected="false"
             data-type="recent"
             data-query="${Utils.escapeHtml(item.query)}"
             tabindex="-1">
          <span class="material-symbols-rounded ai-search-item__icon" aria-hidden="true">history</span>
          <div class="ai-search-item__content">
            <div class="ai-search-item__title">${Utils.escapeHtml(item.query)}</div>
          </div>
          <button type="button" 
                  class="ai-search-remove-btn" 
                  data-query="${Utils.escapeHtml(item.query)}"
                  aria-label="Remove ${Utils.escapeHtml(item.query)} from history">
            <span class="material-symbols-rounded" aria-hidden="true">close</span>
          </button>
        </div>
      `).join('');

      this.resultsContainer.innerHTML = `
        <div class="ai-search-section" role="group" aria-label="Recent searches">
          <div class="ai-search-section-header">
            <span class="material-symbols-rounded" aria-hidden="true">history</span>
            <span class="ai-search-section-title">Recent Searches</span>
            <button type="button" class="ai-search-clear-all" aria-label="Clear all recent searches">
              Clear all
            </button>
          </div>
          <div class="ai-search-section-content">
            ${items}
          </div>
        </div>
      `;

      this.open();
    }

    showTrendingSearches() {
      if (!this.trendingSearches || this.trendingSearches.length === 0) return;

      const items = this.trendingSearches.slice(0, CONFIG.MAX_TRENDING_SEARCHES).map((item, index) => `
        <div class="ai-search-item ai-search-item--trending" 
             role="option"
             id="${this.id}-trending-${index}"
             aria-selected="false"
             data-type="trending"
             data-query="${Utils.escapeHtml(item.query || item)}"
             tabindex="-1">
          <span class="material-symbols-rounded ai-search-item__icon" aria-hidden="true">trending_up</span>
          <div class="ai-search-item__content">
            <div class="ai-search-item__title">${Utils.escapeHtml(item.query || item)}</div>
          </div>
        </div>
      `).join('');

      this.resultsContainer.innerHTML = `
        <div class="ai-search-section" role="group" aria-label="Trending searches">
          <div class="ai-search-section-header">
            <span class="material-symbols-rounded" aria-hidden="true">trending_up</span>
            <span class="ai-search-section-title">Trending</span>
          </div>
          <div class="ai-search-section-content">
            ${items}
          </div>
        </div>
      `;

      this.open();
    }

    showLoading() {
      this.loadingIndicator.hidden = false;
    }

    showError(message) {
      this.resultsContainer.innerHTML = `
        <div class="ai-search-error" role="alert">
          <span class="material-symbols-rounded ai-search-error__icon" aria-hidden="true">error</span>
          <p class="ai-search-error__message">${Utils.escapeHtml(message)}</p>
          <button type="button" class="ai-search-error__retry" onclick="this.closest('.ai-search-wrapper').__aiSearch.retry()">
            <span class="material-symbols-rounded" aria-hidden="true">refresh</span>
            Try again
          </button>
        </div>
      `;
      this.open();
    }

    // ========================================================================
    // SELECTION & NAVIGATION
    // ========================================================================

    selectItem(item) {
      const type = item.dataset.type;
      const url = item.dataset.url;
      const query = item.dataset.query;
      const id = item.dataset.id;
      const position = parseInt(item.dataset.position) || 0;

      // Track click
      this.analytics.trackClick(type, id, this.state.currentQuery, position);

      // Handle different item types
      switch (type) {
        case 'product':
        case 'category':
          this.history.add(this.state.currentQuery);
          this.close();
          
          if (this.onSelect) {
            this.onSelect({
              type,
              id,
              url,
              query: this.state.currentQuery
            });
          }
          
          // Navigate to URL
          if (url) {
            window.location.href = url;
          }
          break;

        case 'suggestion':
        case 'recent':
        case 'trending':
          this.input.value = query;
          this.state.currentQuery = query;
          this.executeSearch(query);
          break;

        case 'view-all':
          this.performSearch(this.state.currentQuery);
          break;
      }
    }

    updateFocus(items) {
      items.forEach((item, index) => {
        const isFocused = index === this.state.focusIndex;
        item.setAttribute('aria-selected', isFocused ? 'true' : 'false');
        item.classList.toggle('ai-search-item--focused', isFocused);

        if (isFocused) {
          this.input.setAttribute('aria-activedescendant', item.id);
          item.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        }
      });

      if (this.state.focusIndex < 0) {
        this.input.removeAttribute('aria-activedescendant');
      }
    }

    performSearch(query) {
      if (!query) return;

      this.history.add(query);
      this.close();

      // Callback or navigate
      if (this.onSearch) {
        this.onSearch(query);
      } else {
        window.location.href = `/products/?q=${encodeURIComponent(query)}`;
      }
    }

    // ========================================================================
    // STATE MANAGEMENT
    // ========================================================================

    open() {
      if (this.state.isOpen) return;

      this.state.isOpen = true;
      this.resultsContainer.hidden = false;
      this.input.setAttribute('aria-expanded', 'true');
      this.container.classList.add('ai-search--open');
    }

    close() {
      if (!this.state.isOpen) return;

      this.state.isOpen = false;
      this.state.focusIndex = -1;
      this.resultsContainer.hidden = true;
      this.input.setAttribute('aria-expanded', 'false');
      this.input.removeAttribute('aria-activedescendant');
      this.container.classList.remove('ai-search--open');
      this.debouncedSearch.cancel();
    }

    announce(message) {
      if (this.liveRegion) {
        this.liveRegion.textContent = message;
      }
    }

    retry() {
      if (this.state.currentQuery) {
        this.executeSearch(this.state.currentQuery);
      }
    }

    // ========================================================================
    // PUBLIC API
    // ========================================================================

    /**
     * Programmatically perform a search
     */
    search(query) {
      this.input.value = query;
      this.state.currentQuery = query;
      this.executeSearch(query);
    }

    /**
     * Clear the search input and results
     */
    clear() {
      this.input.value = '';
      this.state.currentQuery = '';
      this.close();
    }

    /**
     * Focus the search input
     */
    focus() {
      this.input.focus();
    }

    /**
     * Get current search metrics
     */
    getMetrics() {
      return {
        ...this.metrics,
        cacheStats: this.cache.getStats()
      };
    }

    /**
     * Clear the search cache
     */
    clearCache() {
      this.cache.clear();
    }

    /**
     * Get voice search state
     */
    getVoiceState() {
      return this.voiceSearch.getState();
    }

    /**
     * Update configuration
     */
    configure(options) {
      Utils.deepMerge(this.options, options);
    }

    defaultOnSelect(data) {
      // Default behavior - navigate to URL
      if (data.url) {
        window.location.href = data.url;
      }
    }

    /**
     * Destroy the instance and clean up
     */
    destroy() {
      this.requestManager.abortAll();
      this.analytics.destroy();
      this.debouncedSearch.cancel();
      
      if (this.resultsContainer) {
        this.resultsContainer.remove();
      }
      if (this.liveRegion) {
        this.liveRegion.remove();
      }
      if (this.loadingIndicator) {
        this.loadingIndicator.remove();
      }
      if (this.voiceButton) {
        this.voiceButton.remove();
      }

      // Remove wrapper reference
      if (this.container.__aiSearch) {
        delete this.container.__aiSearch;
      }
    }
  }

  // ============================================================================
  // AUTO-INITIALIZATION
  // ============================================================================

  document.addEventListener('DOMContentLoaded', () => {
    // Initialize navbar search
    const navSearchInput = document.querySelector('.nav-search-input');
    if (navSearchInput) {
      const instance = new AISearch(navSearchInput, {
        MIN_CHARS: 2,
        DEBOUNCE_TIME: 250,
        MAX_RESULTS: 10,
        FEATURES: {
          voiceSearch: true,
          trendingSearches: true,
          searchHistory: true,
          analytics: true,
          showCategories: true
        }
      });

      // Store reference for external access
      window.aiSearch = instance;
      const wrapper = navSearchInput.closest('.ai-search-wrapper') || navSearchInput.closest('.nav-search-wrapper');
      if (wrapper) {
        wrapper.__aiSearch = instance;
      }
    }

    // Initialize any elements with data-ai-search attribute
    document.querySelectorAll('[data-ai-search]').forEach(input => {
      const options = {
        MIN_CHARS: parseInt(input.dataset.minChars) || CONFIG.MIN_CHARS,
        MAX_RESULTS: parseInt(input.dataset.maxResults) || CONFIG.MAX_RESULTS,
        FEATURES: {
          voiceSearch: input.dataset.voice !== 'false',
          searchHistory: input.dataset.history !== 'false'
        }
      };

      const instance = new AISearch(input, options);
      const wrapper = input.closest('.ai-search-wrapper');
      if (wrapper) {
        wrapper.__aiSearch = instance;
      }
    });
  });

  return AISearch;
});
