/**
 * PackAxis Enterprise Cart System
 * A robust, production-ready shopping cart with persistence, validation,
 * analytics events, undo support, and server sync capabilities.
 * @version 2.0.0
 */
const Cart = (() => {
  'use strict';

  // Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
  // Configuration
  // Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
  const CONFIG = {
    STORAGE_KEY: 'packaxis_cart',
    METADATA_KEY: 'packaxis_cart_meta',
    VERSION: '2.0.0',
    MAX_QUANTITY_PER_ITEM: 999,
    MAX_ITEMS: 100,
    CART_EXPIRY_DAYS: 30,
    TAX_RATE: 0.13,
    CURRENCY: 'CAD',
    DEBOUNCE_MS: 150,
    SYNC_ENDPOINT: '/api/cart/sync/',
    PLACEHOLDER_SVG: 'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%2248%22 height=%2248%22 viewBox=%220 0 24 24%22 fill=%22none%22 stroke=%22%23b0b8c0%22 stroke-width=%221.5%22%3E%3Crect x=%223%22 y=%223%22 width=%2218%22 height=%2218%22 rx=%222%22/%3E%3Ccircle cx=%228.5%22 cy=%228.5%22 r=%221.5%22/%3E%3Cpolyline points=%2221 15 16 10 5 21%22/%3E%3C/svg%3E',
  };

  // Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
  // State
  // Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
  let _cache = null;
  let _undoStack = [];
  let _listeners = [];
  let _debounceTimer = null;
  let _syncInProgress = false;

  // Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
  // Utility Functions
  // Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
  const utils = {
    generateId: () => `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
    
    sanitize: (str) => {
      if (typeof str !== 'string') return '';
      const div = document.createElement('div');
      div.textContent = str;
      return div.innerHTML;
    },

    formatCurrency: (amount, currency = CONFIG.CURRENCY) => {
      return new Intl.NumberFormat('en-CA', {
        style: 'currency',
        currency,
      }).format(amount);
    },

    debounce: (fn, ms = CONFIG.DEBOUNCE_MS) => {
      return (...args) => {
        clearTimeout(_debounceTimer);
        _debounceTimer = setTimeout(() => fn.apply(null, args), ms);
      };
    },

    isValidProduct: (product) => {
      return (
        product &&
        typeof product.productId !== 'undefined' &&
        typeof product.productName === 'string' &&
        product.productName.trim() !== '' &&
        typeof product.price === 'number' &&
        !isNaN(product.price) &&
        product.price >= 0
      );
    },

    clamp: (value, min, max) => Math.min(Math.max(value, min), max),

    getCSRFToken: () => {
      const meta = document.querySelector('meta[name="csrf-token"]');
      return meta ? meta.getAttribute('content') : '';
    },
  };

  // Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
  // Storage Layer (with expiry & versioning)
  // Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
  const storage = {
    getMetadata() {
      try {
        const raw = localStorage.getItem(CONFIG.METADATA_KEY);
        return raw ? JSON.parse(raw) : null;
      } catch {
        return null;
      }
    },

    setMetadata(data) {
      try {
        localStorage.setItem(CONFIG.METADATA_KEY, JSON.stringify({
          ...data,
          version: CONFIG.VERSION,
          updatedAt: Date.now(),
        }));
      } catch (e) {
        console.warn('[Cart] Metadata save failed:', e);
      }
    },

    getItems() {
      if (_cache !== null) return _cache;

      try {
        const meta = this.getMetadata();
        // Check expiry
        if (meta && meta.createdAt) {
          const expiryMs = CONFIG.CART_EXPIRY_DAYS * 24 * 60 * 60 * 1000;
          if (Date.now() - meta.createdAt > expiryMs) {
            this.clear();
            return [];
          }
        }

        const raw = localStorage.getItem(CONFIG.STORAGE_KEY);
        const items = raw ? JSON.parse(raw) : [];
        // Validate each item
        _cache = items.filter(item => utils.isValidProduct(item));
        return _cache;
      } catch (e) {
        console.error('[Cart] Storage read error:', e);
        return [];
      }
    },

    setItems(items) {
      try {
        _cache = items;
        localStorage.setItem(CONFIG.STORAGE_KEY, JSON.stringify(items));

        const meta = this.getMetadata() || {};
        this.setMetadata({
          ...meta,
          createdAt: meta.createdAt || Date.now(),
          itemCount: items.length,
        });

        return true;
      } catch (e) {
        console.error('[Cart] Storage write error:', e);
        notifications.show('Unable to save cart. Storage may be full.', 'error');
        return false;
      }
    },

    clear() {
      _cache = null;
      localStorage.removeItem(CONFIG.STORAGE_KEY);
      localStorage.removeItem(CONFIG.METADATA_KEY);
    },
  };

  // Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
  // Enterprise Notifications System - Premium Design
  // Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
  const notifications = {
    container: null,
    toastCount: 0,

    init() {
      if (this.container) return;
      this.container = document.createElement('div');
      this.container.className = 'cart-notifications';
      this.container.setAttribute('aria-live', 'polite');
      this.container.setAttribute('role', 'status');
      this.container.setAttribute('aria-atomic', 'false');
      document.body.appendChild(this.container);
    },

    show(message, type = 'success', duration = 3500, action = null) {
      this.init();

      // Limit concurrent toasts
      const existing = this.container.querySelectorAll('.cart-toast:not(.cart-toast--exit)');
      if (existing.length >= 3) {
        this.dismiss(existing[0].dataset.id);
      }

      const id = utils.generateId();
      const toast = document.createElement('div');
      toast.className = `cart-toast cart-toast--${type}`;
      toast.setAttribute('role', 'alert');
      toast.dataset.id = id;
      toast.style.setProperty('--toast-duration', `${duration}ms`);

      // Premium Material Icons
      const icons = {
        success: '<span class="material-symbols-rounded">check_circle</span>',
        error: '<span class="material-symbols-rounded">error</span>',
        info: '<span class="material-symbols-rounded">info</span>',
        warning: '<span class="material-symbols-rounded">warning</span>',
      };

      toast.innerHTML = `
        <span class="cart-toast__icon" aria-hidden="true">${icons[type] || icons.info}</span>
        <span class="cart-toast__message">${utils.sanitize(message)}</span>
        ${action ? `<button class="cart-toast__action" data-action="${action.id}">${utils.sanitize(action.label)}</button>` : ''}
        <button class="cart-toast__close" aria-label="Dismiss notification" type="button">
          <span class="material-symbols-rounded">close</span>
        </button>
      `;

      // Timer management with pause on hover
      let timeoutId;
      let remainingTime = duration;
      let startTime = Date.now();

      const startTimer = () => {
        startTime = Date.now();
        if (remainingTime > 0) {
          timeoutId = setTimeout(() => this.dismiss(id), remainingTime);
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
      toast.querySelector('.cart-toast__close').addEventListener('click', () => {
        if (timeoutId) clearTimeout(timeoutId);
        this.dismiss(id);
      });

      // Action button handler
      if (action) {
        toast.querySelector('.cart-toast__action').addEventListener('click', () => {
          if (timeoutId) clearTimeout(timeoutId);
          action.callback();
          this.dismiss(id);
        });
      }

      this.container.appendChild(toast);

      // Start auto-dismiss timer
      if (duration > 0) {
        startTimer();
      }

      return id;
    },

    dismiss(id) {
      const toast = this.container?.querySelector(`[data-id="${id}"]`);
      if (toast && !toast.classList.contains('cart-toast--exit')) {
        toast.classList.add('cart-toast--exit');
        setTimeout(() => toast.remove(), 350);
      }
    },

    clear() {
      if (this.container) this.container.innerHTML = '';
    },
  };

  // Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
  // Analytics / Event Tracking
  // Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
  const analytics = {
    track(event, data = {}) {
      const payload = {
        event,
        timestamp: new Date().toISOString(),
        cartId: storage.getMetadata()?.cartId || 'anonymous',
        ...data,
      };

      // Google Analytics 4
      if (typeof gtag === 'function') {
        gtag('event', event, payload);
      }

      // Custom event for integrations
      window.dispatchEvent(new CustomEvent('cart:analytics', { detail: payload }));

      // Debug logging in development
      if (window.location.hostname === 'localhost') {
        console.debug('[Cart Analytics]', event, payload);
      }
    },

    trackAddToCart(item, quantity) {
      this.track('add_to_cart', {
        currency: CONFIG.CURRENCY,
        value: item.price * quantity,
        items: [{
          item_id: item.productId,
          item_name: item.productName,
          price: item.price,
          quantity,
        }],
      });
    },

    trackRemoveFromCart(item) {
      this.track('remove_from_cart', {
        currency: CONFIG.CURRENCY,
        value: item.price * item.quantity,
        items: [{
          item_id: item.productId,
          item_name: item.productName,
          price: item.price,
          quantity: item.quantity,
        }],
      });
    },

    trackViewCart(items, totals) {
      this.track('view_cart', {
        currency: CONFIG.CURRENCY,
        value: totals.subtotal,
        items: items.map(i => ({
          item_id: i.productId,
          item_name: i.productName,
          price: i.price,
          quantity: i.quantity,
        })),
      });
    },

    trackBeginCheckout(items, totals) {
      this.track('begin_checkout', {
        currency: CONFIG.CURRENCY,
        value: totals.total,
        items: items.map(i => ({
          item_id: i.productId,
          item_name: i.productName,
          price: i.price,
          quantity: i.quantity,
        })),
      });
    },
  };

  // Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
  // Core Cart Operations
  // Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
  const core = {
    getItems() {
      return JSON.parse(JSON.stringify(storage.getItems()));
    },
    saveItems(items, options = {}) {
      const { silent = false, skipUndo = false } = options;
      if (!skipUndo) {
        const storageState = localStorage.getItem(CONFIG.STORAGE_KEY) || '[]';
        _undoStack.push(storageState);
        if (_undoStack.length > 10) _undoStack.shift();
      }
      const success = storage.setItems(items);
      
      if (!silent) {
        this.emitChange();
        ui.update();
      }

      return success;
    },

    addItem(productId, productName, price, image, quantity = 1, options = {}) {
      const { showNotification = true, maxQty = CONFIG.MAX_QUANTITY_PER_ITEM } = options;

      // Validate inputs
      productId = parseInt(productId, 10);
      price = parseFloat(price);
      quantity = parseInt(quantity, 10);

      if (isNaN(productId) || isNaN(price) || isNaN(quantity)) {
        notifications.show('Invalid product data', 'error');
        return false;
      }

      if (quantity < 1) quantity = 1;

      const items = this.getItems();

      // Check max items limit
      if (items.length >= CONFIG.MAX_ITEMS && !items.find(i => i.productId === productId)) {
        notifications.show(`Cart limit reached (${CONFIG.MAX_ITEMS} items max)`, 'warning');
        return false;
      }

      const safeImage = image && image.trim() ? image : CONFIG.PLACEHOLDER_SVG;
      const existingIndex = items.findIndex(i => i.productId === productId);

      if (existingIndex > -1) {
        const newQty = utils.clamp(items[existingIndex].quantity + quantity, 1, maxQty);
        if (newQty === items[existingIndex].quantity) {
          notifications.show(`Maximum quantity (${maxQty}) reached`, 'warning');
          return false;
        }
        items[existingIndex].quantity = newQty;
        items[existingIndex].updatedAt = Date.now();
        if (!items[existingIndex].image) items[existingIndex].image = safeImage;
      } else {
        items.push({
          productId,
          productName: productName.trim(),
          price,
          image: safeImage,
          quantity: utils.clamp(quantity, 1, maxQty),
          addedAt: Date.now(),
          updatedAt: Date.now(),
        });
      }

      this.saveItems(items);

      // Analytics
      analytics.trackAddToCart({ productId, productName, price }, quantity);

      // Notification with undo
      if (showNotification) {
        notifications.show(`${utils.sanitize(productName)} added to cart`, 'success', 4000,);
      }

      return true;
    },

    removeItem(productId, options = {}) {
      const { showNotification = true } = options;
      productId = parseInt(productId, 10);

      const items = this.getItems();
      const itemIndex = items.findIndex(i => i.productId === productId);

      if (itemIndex === -1) return false;

      const removedItem = items[itemIndex];
      items.splice(itemIndex, 1);
      this.saveItems(items);

      analytics.trackRemoveFromCart(removedItem);

      if (showNotification) {
        notifications.show(`${utils.sanitize(removedItem.productName)} removed`, 'info', 4000, {
          id: 'undo',
          label: 'Undo',
          callback: () => core.undo(),
        });
      }

      return true;
    },

    updateQuantity(productId, quantity, options = {}) {
      const { showNotification = false } = options;
      productId = parseInt(productId, 10);
      quantity = parseInt(quantity, 10);

      if (isNaN(quantity)) return false;

      if (quantity <= 0) {
        return this.removeItem(productId, options);
      }

      const items = this.getItems();
      const item = items.find(i => i.productId === productId);

      if (!item) return false;

      const clampedQty = utils.clamp(quantity, 1, CONFIG.MAX_QUANTITY_PER_ITEM);
      if (clampedQty === item.quantity) return false;

      item.quantity = clampedQty;
      item.updatedAt = Date.now();
      this.saveItems(items);

      if (showNotification) {
        notifications.show('Quantity updated', 'success', 2000);
      }

      return true;
    },

    getTotals() {
      const items = this.getItems();
      const subtotal = items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
      const tax = subtotal * CONFIG.TAX_RATE;
      const total = subtotal + tax;

      return {
        subtotal: parseFloat(subtotal.toFixed(2)),
        tax: parseFloat(tax.toFixed(2)),
        total: parseFloat(total.toFixed(2)),
        itemCount: items.reduce((sum, item) => sum + item.quantity, 0),
        uniqueItems: items.length,
        currency: CONFIG.CURRENCY,
        formattedSubtotal: utils.formatCurrency(subtotal),
        formattedTax: utils.formatCurrency(tax),
        formattedTotal: utils.formatCurrency(total),
      };
    },

    clear(options = {}) {
      const { showNotification = true } = options;
      const currentItems = this.getItems();
      const hadItems = currentItems.length > 0;

      // Save current state to undo stack before clearing
      if (hadItems) {
        _undoStack.push(JSON.stringify(currentItems));
        if (_undoStack.length > 10) _undoStack.shift();
      }

      storage.clear();
      this.emitChange();
      ui.update();

      if (hadItems && showNotification) {
        notifications.show('Cart cleared', 'info', 4000,);
      }
    },

    undo() { window.__undoCalls = (window.__undoCalls || 0) + 1;
      if (_undoStack.length === 0) {
        notifications.show('Nothing to undo', 'info');
        return false;
      }

      const previousState = _undoStack.pop();
      const items = JSON.parse(previousState);
      this.saveItems(items, { skipUndo: true });
      notifications.show('Action undone', 'success');
      return true;
    },

    // Event system for external integrations
    onChange(callback) {
      if (typeof callback === 'function') {
        _listeners.push(callback);
        return () => {
          _listeners = _listeners.filter(cb => cb !== callback);
        };
      }
    },

    emitChange() {
      const items = this.getItems();
      const totals = this.getTotals();
      _listeners.forEach(cb => {
        try { cb({ items, totals }); } catch (e) { console.error('[Cart] Listener error:', e); }
      });
      window.dispatchEvent(new CustomEvent('cart:change', { detail: { items, totals } }));
    },
  };

  // Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
  // Server Sync (for logged-in users)
  // Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
  const sync = {
    async push() {
      if (_syncInProgress) return;
      _syncInProgress = true;

      try {
        const items = core.getItems();
        const response = await fetch(CONFIG.SYNC_ENDPOINT, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': utils.getCSRFToken(),
          },
          body: JSON.stringify({ items }),
          credentials: 'same-origin',
        });

        if (!response.ok) throw new Error('Sync failed');

        const data = await response.json();
        if (data.merged) {
          storage.setItems(data.items);
          ui.update();
        }
      } catch (e) {
        // Silent fail for sync - cart still works locally
        console.warn('[Cart] Sync push failed:', e);
      } finally {
        _syncInProgress = false;
      }
    },

    async pull() {
      if (_syncInProgress) return;
      _syncInProgress = true;

      try {
        const response = await fetch(CONFIG.SYNC_ENDPOINT, {
          method: 'GET',
          credentials: 'same-origin',
        });

        if (!response.ok) throw new Error('Sync pull failed');

        const data = await response.json();
        if (data.items && data.items.length > 0) {
          // Merge server cart with local
          const localItems = core.getItems();
          const mergedItems = this.mergeItems(localItems, data.items);
          storage.setItems(mergedItems);
          ui.update();
        }
      } catch (e) {
        console.warn('[Cart] Sync pull failed:', e);
      } finally {
        _syncInProgress = false;
      }
    },

    mergeItems(local, server) {
      const merged = [...local];
      server.forEach(serverItem => {
        const localIndex = merged.findIndex(l => l.productId === serverItem.productId);
        if (localIndex === -1) {
          merged.push(serverItem);
        } else {
          // Keep the one with higher quantity or more recent update
          const localItem = merged[localIndex];
          if (serverItem.updatedAt > (localItem.updatedAt || 0)) {
            merged[localIndex] = serverItem;
          }
        }
      });
      return merged;
    },
  };

  // Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
  // UI Rendering
  // Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
  const ui = {
    update: utils.debounce(() => {
      ui.updateBadge();
      ui.updateDropdown();
      ui.setupAddToCartButtons();
      if (window.location.pathname === '/checkout/') {
        ui.renderCartPage();
      }
    }, 50),

    updateBadge() {
      const totals = core.getTotals();
      const badge = document.getElementById('cart-badge');
      if (badge) {
        badge.textContent = totals.itemCount > 99 ? '99+' : totals.itemCount;
        badge.classList.toggle('is-hidden', totals.itemCount === 0);
        badge.setAttribute('aria-label', `${totals.itemCount} items in cart`);
      }
    },

    updateDropdown() {
      const dropdown = document.querySelector('.crt-dropdown__inner');
      if (!dropdown) return;

      const items = core.getItems();
      const totals = core.getTotals();

      if (items.length === 0) {
        dropdown.innerHTML = `
          <div class="crt-empty">
            <div class="crt-empty__icon">
              <span class="material-symbols-rounded">shopping_bag</span>
            </div>
            <h4 class="crt-empty__title">Your cart is empty</h4>
            <p class="crt-empty__text">Add items to get started</p>
            <a href="/products/" class="crt-empty__btn">
              <span class="material-symbols-rounded">storefront</span>
              Browse Products
            </a>
          </div>
        `;
        return;
      }

      const displayItems = items.slice(0, 3);
      const remainingCount = items.length - 3;

      const itemsHtml = displayItems.map(item => `
        <div class="crt-item" data-product-id="${item.productId}">
          <div class="crt-item__image">
            <img src="${utils.sanitize(item.image || CONFIG.PLACEHOLDER_SVG)}" 
                 alt="${utils.sanitize(item.productName)}" 
                 loading="lazy"
                 onerror="this.src='${CONFIG.PLACEHOLDER_SVG}'">
          </div>
          <div class="crt-item__content">
            <div class="crt-item__name" title="${utils.sanitize(item.productName)}">${utils.sanitize(item.productName)}</div>
            <div class="crt-item__meta">
              <span class="crt-item__qty">${item.quantity}&times;</span>
              <span class="crt-item__price">${utils.formatCurrency(item.price)}</span>
            </div>
          </div>
          <div class="crt-item__total">${utils.formatCurrency(item.price * item.quantity)}</div>
          <button class="crt-item__remove" data-remove="${item.productId}" aria-label="Remove ${utils.sanitize(item.productName)}">
            <span class="material-symbols-rounded">close</span>
          </button>
        </div>
      `).join('');

      const moreHtml = remainingCount > 0 
        ? `<div class="crt-more">+${remainingCount} more item${remainingCount > 1 ? 's' : ''} in cart</div>` 
        : '';

      dropdown.innerHTML = `
        <div class="crt-header">
          <div class="crt-header__title">
            <span class="material-symbols-rounded">shopping_cart</span>
            Shopping Cart
          </div>
          <span class="crt-header__count">${totals.itemCount}</span>
        </div>
        <div class="crt-items">
          ${itemsHtml}
          ${moreHtml}
        </div>
        <div class="crt-footer">
          <div class="crt-summary">
            <div class="crt-summary__row">
              <span>Subtotal</span>
              <span>${totals.formattedSubtotal}</span>
            </div>
            <div class="crt-summary__row crt-summary__row--total">
              <span>Estimated Total</span>
              <span class="crt-summary__total">${totals.formattedTotal}</span>
            </div>
          </div>
          <a href="/cart/" class="crt-checkout-btn">
            <span class="material-symbols-rounded">shopping_cart_checkout</span>
            View Cart & Checkout
          </a>
          <p class="crt-footer__note">
            <span class="material-symbols-rounded">local_shipping</span>
            Free shipping on orders over $50
          </p>
        </div>
      `;

      // Attach remove handlers
      dropdown.querySelectorAll('[data-remove]').forEach(btn => {
        btn.addEventListener('click', (e) => {
          e.preventDefault();
          e.stopPropagation();
          core.removeItem(btn.dataset.remove);
        });
      });

      // Track checkout click
      dropdown.querySelector('[data-checkout-btn]')?.addEventListener('click', () => {
        analytics.trackBeginCheckout(items, totals);
      });
    },

    setupAddToCartButtons() {
      document.querySelectorAll('[data-add-to-cart]').forEach(btn => {
        if (btn.dataset.cartBound) return;
        btn.dataset.cartBound = 'true';

        btn.addEventListener('click', (e) => {
          e.preventDefault();

          const productId = btn.dataset.productId;
          const productName = btn.dataset.productName;
          const price = btn.dataset.price;
          const image = btn.dataset.image || '';
          const qtySelector = btn.dataset.qtySelector;
          const quantity = qtySelector 
            ? parseInt(document.querySelector(qtySelector)?.value || 1, 10) 
            : 1;

          // Button feedback
          const originalText = btn.innerHTML;
          btn.disabled = true;
          btn.innerHTML = '<span class="cart-btn-loading"></span> Adding...';

          setTimeout(() => {
            core.addItem(productId, productName, parseFloat(price), image, quantity);
            btn.disabled = false;
            btn.innerHTML = originalText;
          }, 300);
        });
      });
    },

    renderCartPage() {
      const items = core.getItems();
      const totals = core.getTotals();
      const container = document.getElementById('cart-items-container');
      if (!container) return;

      // Track view cart
      analytics.trackViewCart(items, totals);

      if (items.length === 0) {
        container.innerHTML = `
          <div class="cart-empty">
            <div class="cart-empty__icon">
              <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                <circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/>
                <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>
              </svg>
            </div>
            <h2 class="cart-empty__title">Your cart is empty</h2>
            <p class="cart-empty__subtitle">Looks like you haven't added any eco-friendly packaging yet.</p>
            <a href="/products/" class="btn btn-primary btn-lg">Browse Products</a>
          </div>
        `;
        return;
      }

      const itemsHtml = items.map((item, index) => `
        <article class="cart-item" data-product-id="${item.productId}" data-index="${index}">
          <div class="cart-item__image">
            <img src="${utils.sanitize(item.image || CONFIG.PLACEHOLDER_SVG)}" 
                 alt="${utils.sanitize(item.productName)}"
                 loading="${index < 3 ? 'eager' : 'lazy'}"
                 onerror="this.src='${CONFIG.PLACEHOLDER_SVG}'">
          </div>
          <div class="cart-item__body">
            <div class="cart-item__info">
              <h3 class="cart-item__title">${utils.sanitize(item.productName)}</h3>
              <p class="cart-item__sku">SKU: ${item.productId}</p>
              <p class="cart-item__unit-price">${utils.formatCurrency(item.price)} each</p>
            </div>
            <div class="cart-item__controls">
              <div class="cart-qty" role="group" aria-label="Quantity controls">
                <button class="cart-qty__btn" data-action="decrease" data-id="${item.productId}" 
                        aria-label="Decrease quantity" ${item.quantity <= 1 ? 'disabled' : ''}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <line x1="5" y1="12" x2="19" y2="12"/>
                  </svg>
                </button>
                <input type="number" class="cart-qty__input" value="${item.quantity}" 
                       min="1" max="${CONFIG.MAX_QUANTITY_PER_ITEM}" 
                       data-id="${item.productId}"
                       aria-label="Quantity">
                <button class="cart-qty__btn" data-action="increase" data-id="${item.productId}" 
                        aria-label="Increase quantity" ${item.quantity >= CONFIG.MAX_QUANTITY_PER_ITEM ? 'disabled' : ''}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
                  </svg>
                </button>
              </div>
              <button class="cart-item__remove" data-remove="${item.productId}">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                </svg>
                Remove
              </button>
            </div>
          </div>
          <div class="cart-item__total">
            <span class="cart-item__total-label">Total</span>
            <span class="cart-item__total-value">${utils.formatCurrency(item.price * item.quantity)}</span>
          </div>
        </article>
      `).join('');

      container.innerHTML = `
        <div class="cart-items">
          ${itemsHtml}
        </div>
        <div class="cart-actions">
          <button class="cart-actions__clear" data-clear-cart>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            </svg>
            Clear Cart
          </button>
        </div>
      `;

      // Attach event handlers
      this.attachCartPageHandlers(container, items);

      // Update summary
      this.updateCartSummary(totals);
    },

    attachCartPageHandlers(container, items) {
      // Quantity decrease
      container.querySelectorAll('[data-action="decrease"]').forEach(btn => {
        btn.addEventListener('click', () => {
          const id = parseInt(btn.dataset.id, 10);
          const item = items.find(i => i.productId === id);
          if (item) core.updateQuantity(id, item.quantity - 1);
        });
      });

      // Quantity increase
      container.querySelectorAll('[data-action="increase"]').forEach(btn => {
        btn.addEventListener('click', () => {
          const id = parseInt(btn.dataset.id, 10);
          const item = items.find(i => i.productId === id);
          if (item) core.updateQuantity(id, item.quantity + 1);
        });
      });

      // Quantity input change
      container.querySelectorAll('.cart-qty__input').forEach(input => {
        input.addEventListener('change', (e) => {
          const id = parseInt(input.dataset.id, 10);
          const qty = parseInt(e.target.value, 10);
          if (!isNaN(qty)) core.updateQuantity(id, qty);
        });
      });

      // Remove buttons
      container.querySelectorAll('[data-remove]').forEach(btn => {
        btn.addEventListener('click', () => {
          core.removeItem(parseInt(btn.dataset.remove, 10));
        });
      });

      // Clear cart
      container.querySelector('[data-clear-cart]')?.addEventListener('click', () => {
        if (confirm('Are you sure you want to clear your cart?')) {
          core.clear();
        }
      });
    },

    updateCartSummary(totals) {
      const subtotalEl = document.getElementById('subtotal');
      const taxEl = document.getElementById('tax');
      const totalEl = document.getElementById('total');

      if (subtotalEl) subtotalEl.textContent = totals.formattedSubtotal;
      if (taxEl) taxEl.textContent = totals.formattedTax;
      if (totalEl) totalEl.textContent = totals.formattedTotal;

      // Checkout button tracking
      document.querySelectorAll('[data-checkout-page-btn]').forEach(btn => {
        btn.addEventListener('click', () => {
          analytics.trackBeginCheckout(core.getItems(), totals);
        });
      });
    },
  };

  // Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
  // Initialization
  // Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
  const init = () => {
    // Inject notification styles
    if (!document.getElementById('cart-toast-styles')) {
      const style = document.createElement('style');
      style.id = 'cart-toast-styles';
      style.textContent = `
        .cart-notifications {
          position: fixed;
          top: 20px;
          right: 20px;
          z-index: 10001;
          display: flex;
          flex-direction: column;
          gap: 10px;
          pointer-events: none;
          max-width: 380px;
          width: 100%;
        }
        .cart-toast {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 14px 16px;
          background: var(--white, #fff);
          border-radius: 12px;
          box-shadow: 0 8px 30px rgba(0,0,0,0.12);
          border-left: 4px solid var(--primary, #4a7c59);
          animation: cartToastIn 0.3s ease;
          pointer-events: auto;
        }
        .cart-toast--success { border-left-color: #22c55e; }
        .cart-toast--error { border-left-color: #ef4444; }
        .cart-toast--warning { border-left-color: #f59e0b; }
        .cart-toast--info { border-left-color: #3b82f6; }
        .cart-toast--exit { animation: cartToastOut 0.3s ease forwards; }
        .cart-toast__icon { flex-shrink: 0; }
        .cart-toast--success .cart-toast__icon { color: #22c55e; }
        .cart-toast--error .cart-toast__icon { color: #ef4444; }
        .cart-toast--warning .cart-toast__icon { color: #f59e0b; }
        .cart-toast--info .cart-toast__icon { color: #3b82f6; }
        .cart-toast__message { flex: 1; font-size: 0.925rem; font-weight: 500; color: var(--dark, #1a1a1a); }
        .cart-toast__action {
          padding: 6px 12px;
          background: var(--gray-100, #f3f4f6);
          border: none;
          border-radius: 6px;
          font-size: 0.8rem;
          font-weight: 600;
          cursor: pointer;
          transition: background 0.2s;
        }
        .cart-toast__action:hover { background: var(--gray-200, #e5e7eb); }
        .cart-toast__close {
          padding: 4px;
          background: none;
          border: none;
          font-size: 1.25rem;
          cursor: pointer;
          opacity: 0.5;
          transition: opacity 0.2s;
          line-height: 1;
        }
        .cart-toast__close:hover { opacity: 1; }
        .cart-btn-loading {
          display: inline-block;
          width: 14px;
          height: 14px;
          border: 2px solid currentColor;
          border-right-color: transparent;
          border-radius: 50%;
          animation: cartSpin 0.6s linear infinite;
          vertical-align: middle;
        }
        @keyframes cartToastIn { from { opacity: 0; transform: translateX(100%); } to { opacity: 1; transform: translateX(0); } }
        @keyframes cartToastOut { to { opacity: 0; transform: translateX(100%); } }
        @keyframes cartSpin { to { transform: rotate(360deg); } }
      `;
      document.head.appendChild(style);
    }

    // Initial UI render
    ui.update();

    // Sync for authenticated users
    const isAuthenticated = document.body.classList.contains('user-authenticated');
    if (isAuthenticated) {
      sync.pull();
    }

    // Cross-tab sync
    window.addEventListener('storage', (e) => {
      if (e.key === CONFIG.STORAGE_KEY) {
        _cache = null;
        ui.update();
      }
    });

    // Visibility change (re-sync when tab becomes active)
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible') {
        _cache = null;
        ui.update();
      }
    });
  };

  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
  // Public API
  // Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
  return {
    // Core operations
    getItems: () => core.getItems(),
    addItem: (id, name, price, image, qty, opts) => core.addItem(id, name, price, image, qty, opts),
    removeItem: (id, opts) => core.removeItem(id, opts),
    updateQuantity: (id, qty, opts) => core.updateQuantity(id, qty, opts),
    getTotals: () => core.getTotals(),
    clear: (opts) => core.clear(opts),
    undo: () => core.undo(),

    // Events
    onChange: (cb) => core.onChange(cb),

    // Sync
    sync: {
      push: () => sync.push(),
      pull: () => sync.pull(),
    },

    // UI
    updateUI: () => ui.update(),

    // Utils (exposed for external use)
    utils: {
      formatCurrency: utils.formatCurrency,
      sanitize: utils.sanitize,
    },

    // Config (read-only)
    config: { ...CONFIG },

    // For legacy compatibility
    PLACEHOLDER_SVG: CONFIG.PLACEHOLDER_SVG,
  };
})();

