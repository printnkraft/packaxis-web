/**
 * Mobile Navigation - Hamburger Menu
 * Implements responsive mobile navigation with hamburger toggle
 * WCAG 2.1 AA Compliant: Focus trap, ESC key, ARIA states
 */

(function() {
  'use strict';
  
  // Wait for DOM to be fully loaded
  document.addEventListener('DOMContentLoaded', function() {
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    const body = document.body;
    
    if (!hamburger || !navMenu) {
      console.warn('Mobile nav: Hamburger or nav menu not found');
      return;
    }
    
    // Get all focusable elements within the nav menu
    const getFocusableElements = () => {
      return navMenu.querySelectorAll(
        'a[href], button:not([disabled]), input:not([disabled]), [tabindex]:not([tabindex="-1"])'
      );
    };
    
    // Focus trap for modal navigation
    function trapFocus(event) {
      if (!navMenu.classList.contains('active')) return;
      
      const focusableElements = getFocusableElements();
      const firstFocusable = focusableElements[0];
      const lastFocusable = focusableElements[focusableElements.length - 1];
      
      if (event.key === 'Tab') {
        if (event.shiftKey) {
          // Shift + Tab
          if (document.activeElement === firstFocusable) {
            event.preventDefault();
            lastFocusable.focus();
          }
        } else {
          // Tab
          if (document.activeElement === lastFocusable) {
            event.preventDefault();
            firstFocusable.focus();
          }
        }
      }
    }
    
    // Toggle menu function
    function toggleMenu(forcedState) {
      const shouldOpen = typeof forcedState === 'boolean' 
        ? forcedState 
        : !hamburger.classList.contains('active');
      
      hamburger.classList.toggle('active', shouldOpen);
      navMenu.classList.toggle('active', shouldOpen);
      body.classList.toggle('nav-open', shouldOpen);
      
      // Update ARIA attributes for accessibility
      hamburger.setAttribute('aria-expanded', String(shouldOpen));
      
      // Prevent body scroll when menu is open
      if (shouldOpen) {
        body.style.overflow = 'hidden';
        // Focus the first link for keyboard users
        const firstLink = navMenu.querySelector('.nav-link');
        if (firstLink) {
          setTimeout(() => firstLink.focus(), 100);
        }
        // Add focus trap listener
        document.addEventListener('keydown', trapFocus);
      } else {
        body.style.overflow = '';
        // Remove focus trap listener
        document.removeEventListener('keydown', trapFocus);
        // Return focus to hamburger
        hamburger.focus();
      }
    }
    
    // Close menu function
    function closeMenu() {
      if (navMenu.classList.contains('active')) {
        toggleMenu(false);
      }
    }
    
    // Hamburger click handler
    hamburger.addEventListener('click', () => toggleMenu());
    
    // Hamburger keyboard handler (Enter and Space)
    hamburger.addEventListener('keydown', function(event) {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        toggleMenu();
      }
    });
    
    // ESC key closes menu (WCAG requirement)
    document.addEventListener('keydown', function(event) {
      if (event.key === 'Escape' && navMenu.classList.contains('active')) {
        closeMenu();
      }
    });
    
    // Close menu when clicking nav links
    const navLinks = navMenu.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
      link.addEventListener('click', () => {
        if (window.innerWidth < 768 && navMenu.classList.contains('active')) {
          closeMenu();
        }
      });
    });
    
    // Close menu when clicking outside
    document.addEventListener('click', function(event) {
      const isClickInside = hamburger.contains(event.target) || navMenu.contains(event.target);
      
      if (!isClickInside && navMenu.classList.contains('active')) {
        closeMenu();
      }
    });
    
    // Close menu on window resize to desktop size
    let resizeTimer;
    window.addEventListener('resize', function() {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(function() {
        if (window.innerWidth >= 768 && navMenu.classList.contains('active')) {
          closeMenu();
        }
      }, 250);
    });
    
    // Add ARIA attributes
    hamburger.setAttribute('aria-label', 'Toggle navigation menu');
    hamburger.setAttribute('aria-expanded', 'false');
    hamburger.setAttribute('aria-controls', 'main-navigation');
    hamburger.setAttribute('role', 'button');
    navMenu.setAttribute('id', 'main-navigation');
    navMenu.setAttribute('role', 'navigation');
  });
})();
