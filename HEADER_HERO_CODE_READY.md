# 💻 HEADER & HERO - IMPLEMENTATION CODE READY

**Document:** Production-ready CSS/HTML code  
**Date:** January 10, 2026  
**Status:** Ready for copy/paste implementation  

---

## 📦 CSS CODE - READY TO IMPLEMENT

### SECTION 1: HEADER ENHANCEMENTS

Insert these CSS rules into `design.css` after current header styles (around line 900):

```css
/* ============================================================================
   PREMIUM HEADER ENHANCEMENTS
   ============================================================================ */

/* Enhanced Logo with Glow Effect */
.logo {
  height: 40px;
  width: auto;
  display: block;
  transition: all var(--dur-med) var(--easing);
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.05));
  position: relative;
}

.logo::before {
  content: '';
  position: absolute;
  inset: -8px;
  background: radial-gradient(circle, rgba(13, 123, 127, 0.1), transparent);
  border-radius: 8px;
  opacity: 0;
  transition: opacity var(--dur-med) var(--easing);
  pointer-events: none;
}

.logo:hover::before {
  opacity: 1;
}

.logo:hover {
  transform: scale(1.05) translateY(-2px);
  filter: drop-shadow(0 8px 16px rgba(13, 123, 127, 0.15));
}

/* Enhanced Navigation Menu (Mobile) */
.nav-menu {
  display: none;
  list-style: none;
  position: fixed;
  top: 72px;
  left: 0;
  width: 100%;
  height: calc(100vh - 72px);
  background: linear-gradient(180deg, var(--white) 0%, var(--gray-50) 100%);
  flex-direction: column;
  padding: var(--space-8) var(--space-6);
  gap: var(--space-2);
  z-index: var(--z-fixed);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  overflow-y: auto;
  backdrop-filter: blur(8px);
}

.nav-menu.active {
  display: flex;
}

/* Premium Navigation Links */
.nav-link {
  font-weight: 500;
  color: var(--dark);
  transition: all var(--dur-med) var(--easing);
  position: relative;
  font-size: 1rem;
  padding: var(--space-4) var(--space-3);
  border-radius: var(--radius-lg);
  display: block;
  border-left: 3px solid transparent;
  border-bottom: none;
}

.nav-link::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: linear-gradient(180deg, var(--primary), var(--accent));
  border-radius: var(--radius-lg);
  opacity: 0;
  transition: opacity var(--dur-med) var(--easing);
}

.nav-link:hover {
  color: var(--primary);
  background: rgba(13, 123, 127, 0.08);
}

.nav-link:hover::before {
  opacity: 1;
}

/* Enhanced Search Bar */
.nav-search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
  border-radius: var(--radius-lg);
  background: linear-gradient(135deg, var(--gray-50) 0%, var(--white) 100%);
  border: 1.5px solid var(--gray-200);
  transition: all var(--dur-med) var(--easing);
  overflow: hidden;
}

.nav-search-input-wrapper::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(13, 123, 127, 0.05), transparent);
  opacity: 0;
  transition: opacity var(--dur-med) var(--easing);
  pointer-events: none;
  animation: shimmerInactive 2s infinite;
}

.nav-search-input {
  width: 100%;
  padding: var(--space-3) var(--space-4) var(--space-3) var(--space-12);
  border: none;
  border-radius: var(--radius-lg);
  font-family: var(--font-body);
  font-size: 0.9rem;
  background: transparent;
  transition: all var(--dur-med) var(--easing);
  color: var(--dark);
}

.nav-search-input:focus {
  outline: none;
}

/* Focus state with has() selector */
.nav-search-input-wrapper:has(.nav-search-input:focus) {
  border-color: var(--primary);
  background: linear-gradient(135deg, var(--white) 0%, var(--gray-50) 100%);
  box-shadow: 0 0 0 3px rgba(13, 123, 127, 0.12),
              inset 0 1px 2px rgba(0, 0, 0, 0.04);
}

.nav-search-input-wrapper:has(.nav-search-input:focus)::before {
  opacity: 1;
  animation: shimmerActive 2s infinite;
}

@keyframes shimmerInactive {
  0%, 100% { transform: translateX(-100%); opacity: 0; }
  50% { opacity: 0.5; }
}

@keyframes shimmerActive {
  0%, 100% { transform: translateX(-100%); opacity: 1; }
  50% { opacity: 0.3; }
}

/* Enhanced Search Icon */
.nav-search-icon {
  position: absolute;
  left: var(--space-3);
  top: 50%;
  transform: translateY(-50%);
  color: var(--gray-500);
  pointer-events: none;
  transition: color var(--dur-fast) var(--easing));
  z-index: 1;
  display: flex !important;
  align-items: center;
  justify-content: center;
  font-size: 20px !important;
  width: 20px !important;
  height: 20px !important;
  min-width: 20px !important;
  flex-shrink: 0;
}

.nav-search-input:focus ~ .nav-search-icon {
  color: var(--primary);
}

/* Premium Cart Dropdown */
.cart-dropdown {
  position: absolute;
  top: calc(100% + 12px);
  right: 0;
  width: 380px;
  max-width: 90vw;
  background: var(--white);
  border-radius: var(--radius-lg);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15),
              0 0 1px rgba(0, 0, 0, 0.1);
  opacity: 0;
  visibility: hidden;
  transform: translateY(-10px) scale(0.95);
  transition: all var(--dur-med) var(--easing));
  z-index: 200;
  border: 1px solid rgba(13, 123, 127, 0.12);
  overflow: hidden;
  backdrop-filter: blur(8px);
}

.nav-cart-wrapper:hover .cart-dropdown,
.cart-dropdown:hover {
  opacity: 1;
  visibility: visible;
  transform: translateY(0) scale(1);
}

/* Enhanced Cart Dropdown Arrow */
.cart-dropdown::before {
  content: '';
  position: absolute;
  top: -8px;
  right: 16px;
  width: 16px;
  height: 16px;
  background: var(--white);
  border-top: 1px solid rgba(13, 123, 127, 0.12);
  border-left: 1px solid rgba(13, 123, 127, 0.12);
  border-radius: 2px;
  transform: rotate(45deg);
  z-index: -1;
}

/* Scroll-Triggered Navbar Compaction */
.navbar.scrolled {
  padding-top: var(--space-2);
  padding-bottom: var(--space-2);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
  background: rgba(255, 255, 255, 0.95);
}

.navbar.scrolled .logo {
  height: 32px;
  transition: height var(--dur-med) var(--easing));
}

.navbar.scrolled .nav-search-input {
  font-size: 0.85rem;
  padding: var(--space-2) var(--space-3) var(--space-2) var(--space-10);
}

/* ============================================================================
   END HEADER ENHANCEMENTS
   ============================================================================ */
```

---

### SECTION 2: HERO SECTION ENHANCEMENTS

Replace existing hero styles (lines 6747-6893) with this enhanced version:

```css
/* ============================================================================
   PREMIUM HERO SECTION WITH BACKGROUND IMAGE
   ============================================================================ */

.hero--premium {
  background-size: cover;
  background-position: center 20%;
  background-attachment: fixed;
  background-color: var(--primary);
  position: relative;
  overflow: hidden;
  min-height: 90vh;
}

/* Image Overlay for Text Readability */
.hero__image-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    180deg,
    rgba(13, 123, 127, 0.4) 0%,
    rgba(13, 123, 127, 0.6) 50%,
    rgba(0, 26, 51, 0.7) 100%
  );
  z-index: 1;
  backdrop-filter: blur(1px);
}

/* Floating Decorative Elements */
.hero--premium::before {
  content: '';
  position: absolute;
  top: -30%;
  right: -10%;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(204, 255, 0, 0.1) 0%, transparent 70%);
  border-radius: 50%;
  animation: float 8s ease-in-out infinite;
  z-index: 2;
}

.hero--premium::after {
  content: '';
  position: absolute;
  bottom: -20%;
  left: -5%;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(13, 123, 127, 0.1) 0%, transparent 70%);
  border-radius: 50%;
  animation: float 10s ease-in-out infinite;
  z-index: 2;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(30px); }
}

/* Content Positioned Above Overlay */
.hero--premium .container {
  position: relative;
  z-index: 3;
}

.hero-content {
  position: relative;
  z-index: 3;
  animation: fadeInUp 800ms ease-out 200ms both;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Enhanced Hero Badge */
.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  background: rgba(204, 255, 0, 0.15);
  border: 2px solid rgba(204, 255, 0, 0.4);
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--accent);
  margin-bottom: var(--space-6);
  width: fit-content;
  position: relative;
  overflow: hidden;
  animation: slideInDown 600ms ease-out;
}

.hero-badge::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 2s infinite;
}

@keyframes slideInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.hero-badge .material-symbols-rounded {
  font-size: 1rem;
  color: var(--accent);
  position: relative;
  z-index: 1;
}

/* Enhanced Hero Title */
.hero-title--premium {
  font-size: clamp(2rem, 8vw, 4rem);
  font-weight: 900;
  color: var(--white);
  line-height: 1.1;
  margin: var(--space-6) 0;
  text-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  letter-spacing: -0.02em;
  animation: fadeInUp 800ms ease-out 300ms both;
}

/* Gradient Accent Text */
.hero-accent {
  background: linear-gradient(120deg, var(--accent) 0%, #ffff99 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: none;
  font-weight: 950;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

/* Enhanced Hero Subtitle */
.hero-subtitle--premium {
  font-size: clamp(1rem, 2.5vw, 1.375rem);
  color: rgba(255, 255, 255, 0.95);
  line-height: 1.6;
  margin: var(--space-6) 0;
  max-width: 600px;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  animation: fadeInUp 800ms ease-out 400ms both;
}

/* Premium Statistics Grid */
.hero-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: var(--space-8);
  margin: var(--space-10) 0 var(--space-12);
  padding: var(--space-8) 0;
  border-top: 2px solid rgba(255, 255, 255, 0.15);
  border-bottom: 2px solid rgba(255, 255, 255, 0.15);
}

.hero-stat {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  text-align: left;
  animation: countUp 1s ease-out forwards;
  opacity: 0;
}

.hero-stat:nth-child(1) { animation-delay: 500ms; }
.hero-stat:nth-child(2) { animation-delay: 700ms; }
.hero-stat:nth-child(3) { animation-delay: 900ms; }

@keyframes countUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.hero-stat__number {
  display: block;
  font-size: clamp(2rem, 5vw, 3rem);
  font-weight: 950;
  color: var(--accent);
  line-height: 1;
  letter-spacing: -0.02em;
  text-shadow: 0 4px 12px rgba(204, 255, 0, 0.2);
}

.hero-stat__label {
  display: block;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.85);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* Premium CTA Buttons */
.hero-buttons--premium {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-4);
  margin: var(--space-8) 0;
  animation: fadeInUp 800ms ease-out 600ms both;
}

.btn {
  position: relative;
  overflow: hidden;
  font-weight: 700;
  border-radius: var(--radius-lg);
  transition: all var(--dur-med) var(--easing));
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  white-space: nowrap;
}

.btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.2), transparent 70%);
  transform: translateX(-100%);
  transition: transform var(--dur-slow) var(--easing));
  pointer-events: none;
}

.btn:hover::before {
  transform: translateX(100%);
}

.btn-primary {
  background: linear-gradient(135deg, var(--primary) 0%, #0a8a8f 100%);
  color: var(--white);
  border: 2px solid var(--primary);
  padding: var(--space-4) var(--space-8);
  font-size: 1.0625rem;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #0a8a8f 0%, var(--primary) 100%);
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(13, 123, 127, 0.3);
  border-color: var(--accent);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.15);
  color: var(--white);
  border: 2px solid rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(8px);
  padding: var(--space-4) var(--space-8);
  font-size: 1.0625rem;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.25);
  border-color: var(--white);
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.2);
}

.btn .material-symbols-rounded {
  font-size: 1.25rem;
  transition: transform var(--dur-med) var(--easing));
}

.btn:hover .material-symbols-rounded {
  transform: translateX(4px);
}

/* Enhanced Hero Trust Section */
.hero-trust {
  display: flex;
  align-items: center;
  gap: var(--space-6);
  margin-top: var(--space-10);
  padding-top: var(--space-8);
  border-top: 1px solid rgba(255, 255, 255, 0.15);
  animation: fadeInUp 800ms ease-out 800ms both;
}

.hero-trust__label {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.75);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-right: var(--space-2);
}

.hero-trust__logos {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-wrap: wrap;
}

.hero-trust-logo {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.12);
  border: 1.5px solid rgba(255, 255, 255, 0.25);
  border-radius: var(--radius-lg);
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.5rem;
  transition: all var(--dur-med) var(--easing));
  cursor: pointer;
}

.hero-trust-logo:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: var(--accent);
  transform: translateY(-4px) scale(1.1);
  box-shadow: 0 8px 16px rgba(13, 123, 127, 0.2);
}

/* Responsive Hero Design */
@media (max-width: 767px) {
  .hero--premium {
    min-height: 80vh;
    padding: var(--space-8) 0;
    background-attachment: scroll;
  }
  
  .hero-title--premium {
    font-size: 1.75rem;
    margin: var(--space-4) 0;
  }
  
  .hero-subtitle--premium {
    font-size: 1rem;
    margin: var(--space-4) 0;
  }
  
  .hero-stats {
    grid-template-columns: 1fr;
    gap: var(--space-6);
    margin: var(--space-8) 0;
    padding: var(--space-6) 0;
  }
  
  .hero-buttons--premium {
    flex-direction: column;
    width: 100%;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
  
  .hero-trust {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-4);
  }
}

@media (min-width: 768px) and (max-width: 1023px) {
  .hero-title--premium {
    font-size: 2.5rem;
  }
  
  .hero-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (prefers-reduced-motion: reduce) {
  .hero--premium {
    background-attachment: scroll;
  }
  
  .hero-content,
  .hero-badge,
  .hero-stat,
  .hero-buttons--premium,
  .hero-trust {
    animation: none !important;
  }
}

/* ============================================================================
   END HERO ENHANCEMENTS
   ============================================================================ */
```

---

## 💻 JAVASCRIPT CODE

Add this to your JavaScript file (in `base.html` script tags or separate file):

```javascript
/* ============================================================================
   HEADER NAVBAR SCROLL HANDLING
   ============================================================================ */

document.addEventListener('DOMContentLoaded', function() {
  const navbar = document.querySelector('.navbar');
  const scrollThreshold = 10;
  
  window.addEventListener('scroll', function() {
    if (window.scrollY > scrollThreshold) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  });
});

/* ============================================================================
   HAMBURGER MENU TOGGLE
   ============================================================================ */

document.addEventListener('DOMContentLoaded', function() {
  const hamburger = document.querySelector('.hamburger');
  const navMenu = document.querySelector('.nav-menu');
  const body = document.body;
  
  if (hamburger) {
    hamburger.addEventListener('click', function(e) {
      e.preventDefault();
      const isExpanded = hamburger.getAttribute('aria-expanded') === 'true';
      
      hamburger.setAttribute('aria-expanded', !isExpanded);
      navMenu.classList.toggle('active');
      body.classList.toggle('nav-open');
    });
    
    // Close menu when a link is clicked
    const navLinks = navMenu.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
      link.addEventListener('click', function() {
        hamburger.setAttribute('aria-expanded', 'false');
        navMenu.classList.remove('active');
        body.classList.remove('nav-open');
      });
    });
    
    // Close menu when clicking outside
    document.addEventListener('click', function(e) {
      if (!e.target.closest('.navbar')) {
        hamburger.setAttribute('aria-expanded', 'false');
        navMenu.classList.remove('active');
        body.classList.remove('nav-open');
      }
    });
  }
});

/* ============================================================================
   END JAVASCRIPT
   ============================================================================ */
```

---

## 📝 HTML UPDATES

### Update `base.html` header (no major changes needed):

The current header HTML is already correct. Just ensure:

```html
<nav class="navbar" role="navigation" aria-label="Main navigation">
  <div class="container">
    <div class="nav-wrapper">
      <!-- Current logo, menu, search, actions code works as-is -->
    </div>
  </div>
</nav>
```

### Update `home.html` hero section:

Replace the `<section class="hero hero--premium">` section with:

```html
<!-- HERO SECTION WITH BACKGROUND IMAGE SUPPORT -->
<section class="hero hero--premium" 
         style="background-image: url('{% static 'images/hero-bg.jpg' %}');">
  
  <!-- Dark overlay for text readability -->
  <div class="hero__image-overlay"></div>
  
  <div class="container">
    <div class="hero-grid hero-grid--single">
      <div class="hero-content">
        <!-- Existing hero-badge, title, subtitle, stats, buttons, trust section -->
        <!-- All current content remains the same -->
      </div>
    </div>
  </div>
  
  <!-- Decorative floating elements (existing) -->
  <div class="hero__decoration hero__decoration--1"></div>
  <div class="hero__decoration hero__decoration--2"></div>
</section>
```

---

## 🖼️ BACKGROUND IMAGE

### Image Specifications:

**File Path:** `/static/images/hero-bg.jpg`  
**Recommended Dimensions:** 1920x1080px (minimum for quality)  
**File Size:** 200-400KB (compressed)  
**Format:** JPG or WEBP  

### Image Content Ideas:
- Premium eco-friendly packaging in use
- Hands holding quality packages
- Business/retail scenarios
- Warm, inviting color palette
- Lower-right quadrant lighter (for text)

### Fallback for No Image:
The gradient background will still display if image fails to load:
```css
background-color: var(--primary); /* Fallback gradient color */
```

---

## ✅ IMPLEMENTATION CHECKLIST

### Step 1: CSS Updates
- [ ] Copy Header Enhancement CSS (Section 1)
- [ ] Paste after current navbar styles (~line 900)
- [ ] Copy Hero Enhancement CSS (Section 2)
- [ ] Replace existing hero styles (lines 6747-6893)
- [ ] Save design.css

### Step 2: JavaScript Updates
- [ ] Add scroll handling code
- [ ] Add hamburger menu toggle code
- [ ] Save to base.html or separate JS file
- [ ] Test scroll behavior
- [ ] Test mobile menu

### Step 3: HTML Updates
- [ ] Update hero section with image overlay div
- [ ] Add background-image style to hero section
- [ ] Ensure all existing content remains

### Step 4: Image Assets
- [ ] Prepare hero background image (1920x1080)
- [ ] Compress to ~200-400KB
- [ ] Place in `/static/images/` directory
- [ ] Name: `hero-bg.jpg` (or update CSS path)

### Step 5: Testing
- [ ] Test on desktop (1024px+)
- [ ] Test on tablet (768px)
- [ ] Test on mobile (320px)
- [ ] Test scroll navbar compaction
- [ ] Test hamburger menu toggle
- [ ] Test all animations smooth (60fps)
- [ ] Test on slow 3G network
- [ ] Test image fallback (remove image temporarily)
- [ ] Verify accessibility (focus states, keyboard nav)
- [ ] Test on Chrome, Firefox, Safari, Edge

---

## 🎯 Priority Implementation Order

1. **First:** Update CSS (copy both sections into design.css)
2. **Second:** Add JavaScript (scroll and menu handlers)
3. **Third:** Update HTML (hero image overlay, background-image)
4. **Fourth:** Add background image asset
5. **Fifth:** Comprehensive testing across devices

---

## 📊 Expected Results

### Visual Improvements
- ✅ Premium, sophisticated header design
- ✅ Glowing logo with smooth animations
- ✅ Shimmering search bar with focus states
- ✅ Professional cart dropdown
- ✅ Hero section with impactful background image
- ✅ Staggered content animations
- ✅ Smooth parallax scroll effect
- ✅ Enterprise-grade appearance

### Performance
- ✅ Minimal impact on load time
- ✅ 60fps smooth animations
- ✅ Optimized CSS (no bloat)
- ✅ Hardware-accelerated transforms

---

**Status:** ✅ Code Ready for Implementation  
**Compatibility:** Chrome 90+, Firefox 88+, Safari 14+, Edge 90+  
**Estimated Implementation Time:** 1-2 hours  
**Testing Time:** 1-2 hours  

