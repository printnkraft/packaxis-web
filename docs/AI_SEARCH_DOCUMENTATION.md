# AI-Powered Autocomplete Search Documentation
**Packaxis Packaging Canada**

## Overview
The AI-powered autocomplete search provides intelligent, real-time product and category suggestions as users type in the navbar search bar. This reusable component enhances user experience with keyboard navigation, recent search history, and AI-powered suggestions.

---

## Features

### 🎯 Core Functionality
- **Real-time Autocomplete**: Shows suggestions as users type (min 2 characters)
- **Intelligent Debouncing**: 300ms delay to prevent excessive API calls
- **Smart Caching**: Reduces server load by caching previous search results
- **Recent Searches**: Remembers last 10 searches in localStorage
- **Keyboard Navigation**: Full arrow key, Enter, and Escape support
- **AI Suggestions**: Context-aware keyword suggestions based on search patterns
- **Category Filtering**: Shows matching product categories with product counts
- **Visual Feedback**: Loading states, empty states, and error handling

### 🎨 Premium Design
- **Consistent Styling**: Matches existing cart-dropdown design system
- **Responsive Layout**: Adapts to mobile, tablet, and desktop screens
- **Accessibility**: ARIA labels, keyboard navigation, screen reader support
- **Smooth Animations**: Fade-in effects with cubic-bezier easing
- **Highlighted Matches**: Search terms highlighted in results

---

## Installation & Setup

### 1. File Structure
```
frontend/
├── static/
│   ├── css/
│   │   └── styles.css              # AI search styles added
│   └── js/
│       └── ai-search.js            # New AI search component
└── templates/
    └── base.html                    # Script reference added

backend/
└── apps/
    └── products/
        ├── views.py                 # autocomplete_search endpoint
        └── urls.py                  # /api/products/autocomplete/ route
```

### 2. Backend API Endpoint
**URL**: `/api/products/autocomplete/`  
**Method**: `GET`  
**Parameters**:
- `q` (string, required): Search query (min 2 characters)
- `max` (integer, optional): Maximum results per section (default: 8)

**Response Format**:
```json
{
  "products": [
    {
      "id": 123,
      "name": "Kraft Paper Bags",
      "url": "/products/123/",
      "price": "12.99",
      "category": "Paper Bags",
      "image_url": "/media/products/bag.jpg",
      "thumbnail": "/media/products/bag.jpg",
      "in_stock": true,
      "sku": "PKG-001"
    }
  ],
  "categories": [
    {
      "id": 5,
      "name": "Eco Bags",
      "slug": "eco-bags",
      "url": "/products/?category=eco-bags",
      "product_count": 42
    }
  ],
  "suggestions": [
    {
      "text": "custom kraft bags",
      "reason": "Popular search"
    }
  ],
  "total_count": 156
}
```

### 3. Frontend Integration

#### Automatic Initialization
The AI search automatically initializes on page load for the navbar search input:

```javascript
// In ai-search.js (already configured)
document.addEventListener('DOMContentLoaded', () => {
    const navSearchInput = document.querySelector('.nav-search-input');
    if (navSearchInput) {
        window.aiSearch = new AISearch(navSearchInput, {
            minChars: 2,
            debounceTime: 300,
            maxResults: 8
        });
    }
});
```

#### Reusable Across Pages
Add `data-ai-search` attribute to any search input for automatic initialization:

```html
<!-- Example: Product page search -->
<input 
    type="search" 
    class="product-search-input" 
    data-ai-search 
    data-min-chars="2"
    data-max-results="5"
    placeholder="Search products..."
>
```

#### Manual Initialization
For custom implementations:

```javascript
const searchInput = document.querySelector('#my-search');
const customSearch = new AISearch(searchInput, {
    minChars: 3,
    debounceTime: 500,
    maxResults: 10,
    apiEndpoint: '/api/products/autocomplete/',
    showCategories: true,
    showRecentSearches: true,
    onSelect: (data) => {
        console.log('User selected:', data);
        // Custom action
    }
});
```

---

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `minChars` | number | 2 | Minimum characters before showing suggestions |
| `debounceTime` | number | 300 | Milliseconds to wait before API call |
| `maxResults` | number | 8 | Maximum results per section |
| `apiEndpoint` | string | `/api/products/autocomplete/` | Backend API URL |
| `placeholder` | string | `'Search products, categories...'` | Input placeholder text |
| `showCategories` | boolean | true | Display category suggestions |
| `showRecentSearches` | boolean | true | Show recent search history |
| `onSelect` | function | Default handler | Callback when item selected |

---

## CSS Customization

### Key CSS Classes

```css
/* Main container */
.ai-search-results {
    /* Dropdown positioning, shadows, backdrop blur */
}

/* Section wrapper */
.ai-search-section {
    /* Groups products/categories/suggestions */
}

/* Section title */
.ai-search-section-title {
    /* "Products", "Categories", "AI Suggestions" headers */
}

/* Individual result item */
.ai-search-item {
    /* Clickable search result with hover effects */
}

/* Product-specific elements */
.ai-search-item-image { /* Product thumbnail */ }
.ai-search-item-title { /* Product name with highlights */ }
.ai-search-item-price { /* Price display */ }

/* Badges */
.ai-badge-success { /* In Stock badge */ }
.ai-badge-danger { /* Out of Stock badge */ }

/* States */
.ai-search-loading { /* Loading spinner */ }
.ai-search-empty { /* No results message */ }
.ai-search-error { /* Error message */ }
```

### Responsive Breakpoints
```css
/* Mobile (≤768px) */
@media (max-width: 768px) {
    .ai-search-results {
        max-height: 60vh;
        width: calc(100vw - 2rem);
    }
    
    .ai-search-item-image {
        width: 40px;
        height: 40px;
    }
}
```

---

## API Methods

### Public Methods

```javascript
// Clear search input and hide results
aiSearch.clear();

// Remove the search component entirely
aiSearch.destroy();

// Manually trigger search (for programmatic use)
aiSearch.fetchSuggestions('query string');

// Show/hide results programmatically
aiSearch.showResults();
aiSearch.hideResults();
```

### Event Handling

The component automatically handles:
- **Input events**: Triggers debounced search
- **Focus events**: Shows recent searches or cached results
- **Blur events**: Hides dropdown after delay
- **Keyboard events**: Arrow navigation, Enter to select, Escape to close
- **Click events**: Item selection and recent search removal

---

## AI Suggestions Logic

The backend provides context-aware suggestions based on common packaging industry keywords:

```python
# Example from backend/apps/products/views.py
if 'box' in query.lower():
    suggestions = [
        {'text': 'cardboard boxes', 'reason': 'Popular packaging'},
        {'text': 'custom boxes', 'reason': 'Custom solutions'}
    ]
elif 'tape' in query.lower():
    suggestions = [
        {'text': 'packing tape', 'reason': 'Most searched'},
        {'text': 'custom tape', 'reason': 'Branded options'}
    ]
# ... more patterns
```

### Extending AI Suggestions
To add more intelligent suggestions, enhance the `autocomplete_search` view in [products/views.py](../backend/apps/products/views.py):

1. **Machine Learning Integration**: Connect to ML model for semantic search
2. **User Behavior Tracking**: Analyze click patterns to improve suggestions
3. **Industry-Specific Keywords**: Add more packaging-related keyword patterns
4. **Synonym Mapping**: Include common industry synonyms (e.g., "bag" → "sack", "pouch")

---

## Performance Optimization

### Caching Strategy
```javascript
// Results cached in-memory per query
this.cache = new Map();

// Cache hit example
if (this.cache.has(query)) {
    this.renderResults(this.cache.get(query), query);
    return; // Skip API call
}
```

### Debouncing
```javascript
// Prevents excessive API calls during typing
clearTimeout(this.debounceTimer);
this.debounceTimer = setTimeout(() => {
    this.fetchSuggestions(query);
}, this.options.debounceTime);
```

### Recent Searches (LocalStorage)
```javascript
// Persists across sessions
localStorage.setItem('aiSearchRecent', JSON.stringify(searches));

// Automatic cleanup (max 10 entries)
this.recentSearches = this.recentSearches.slice(0, 10);
```

---

## Accessibility Features

### ARIA Attributes
- `role="combobox"` on input
- `role="listbox"` on results container
- `role="option"` on each result item
- `aria-expanded` indicates dropdown state
- `aria-selected` for keyboard-focused items
- `aria-label` for screen reader descriptions

### Keyboard Navigation
- **Tab**: Focus search input
- **Arrow Down**: Move to next result
- **Arrow Up**: Move to previous result
- **Enter**: Select focused result or perform search
- **Escape**: Close dropdown and blur input

---

## Testing

### Manual Testing Checklist
- [ ] Type 2+ characters → autocomplete appears
- [ ] Type 1 character → no autocomplete
- [ ] Arrow keys navigate through results
- [ ] Enter key selects highlighted result
- [ ] Escape key closes dropdown
- [ ] Click outside closes dropdown
- [ ] Recent searches appear on focus (empty input)
- [ ] Remove button deletes recent search
- [ ] Product images load correctly
- [ ] "In Stock" / "Out of Stock" badges display
- [ ] Price formatting ($XX.XX)
- [ ] "View all results" link works
- [ ] Mobile responsive layout
- [ ] Loading spinner appears during fetch
- [ ] Error message on API failure
- [ ] Empty state for no results

### Backend Testing
```bash
# Test autocomplete endpoint
curl "http://localhost:8000/api/products/autocomplete/?q=bag&max=5"

# Expected response structure:
# {
#   "products": [...],
#   "categories": [...],
#   "suggestions": [...],
#   "total_count": 42
# }
```

---

## Troubleshooting

### Issue: Autocomplete not appearing
**Solution**: 
1. Check browser console for JavaScript errors
2. Verify `ai-search.js` is loaded in [base.html](../frontend/templates/base.html)
3. Ensure input has class `.nav-search-input`
4. Confirm API endpoint returns 200 status

### Issue: API 404 error
**Solution**:
1. Verify URL pattern in [products/urls.py](../backend/apps/products/urls.py)
2. Check Django server is running: `python manage.py runserver`
3. Confirm frontend API path matches backend: `/api/products/autocomplete/`

### Issue: Images not loading
**Solution**:
1. Check `MEDIA_URL` in Django settings
2. Ensure `ProductImage` model has images uploaded
3. Verify image URLs in API response
4. Add fallback placeholder image: `/static/images/placeholder.png`

### Issue: Styling looks broken
**Solution**:
1. Run `npm run build` in frontend directory
2. Clear browser cache (Ctrl+Shift+R)
3. Check [styles.css](../frontend/static/css/styles.css) for AI search classes
4. Verify Vite compiled CSS includes new styles

---

## Browser Support

| Browser | Version | Status |
|---------|---------|--------|
| Chrome | 90+ | ✅ Fully Supported |
| Firefox | 88+ | ✅ Fully Supported |
| Safari | 14+ | ✅ Fully Supported |
| Edge | 90+ | ✅ Fully Supported |
| Mobile Safari | iOS 14+ | ✅ Fully Supported |
| Mobile Chrome | Android 90+ | ✅ Fully Supported |

### Polyfills Required
None. Uses vanilla JavaScript ES6+ features supported by all modern browsers.

---

## Future Enhancements

### Phase 2 (Recommended)
- [ ] **Voice Search**: Integrate Web Speech API for hands-free searching
- [ ] **Image Search**: Upload product images for visual search
- [ ] **Advanced Filters**: Price range, brand, material filters in dropdown
- [ ] **Search Analytics**: Track popular searches, conversion rates
- [ ] **Personalization**: ML-powered recommendations based on user history
- [ ] **Fuzzy Matching**: Typo tolerance (e.g., "papr bag" → "paper bag")
- [ ] **Multi-language**: Support French for Canadian bilingual audience

### Phase 3 (Advanced)
- [ ] **Elasticsearch Integration**: For faster, more relevant search
- [ ] **Natural Language Processing**: Understand queries like "eco-friendly boxes for food"
- [ ] **Related Products**: Show similar items in autocomplete
- [ ] **Trending Searches**: Display popular searches in empty state
- [ ] **Search-as-you-type Highlighting**: Real-time matching while typing

---

## Code Examples

### Example 1: Custom Callback on Selection
```javascript
const searchInput = document.querySelector('.nav-search-input');
new AISearch(searchInput, {
    onSelect: (data) => {
        // Track analytics
        gtag('event', 'search_select', {
            item_type: data.type,
            item_id: data.id,
            search_query: searchInput.value
        });
        
        // Custom navigation
        window.location.href = data.url;
    }
});
```

### Example 2: Multiple Search Instances
```html
<!-- Header search -->
<input type="search" class="nav-search-input" data-ai-search>

<!-- Sidebar search (product page) -->
<input 
    type="search" 
    class="sidebar-search" 
    data-ai-search 
    data-min-chars="1"
    data-max-results="5"
>
```

### Example 3: Programmatic Search
```javascript
// Trigger search from external button
document.querySelector('#custom-search-btn').addEventListener('click', () => {
    const query = document.querySelector('#custom-input').value;
    window.aiSearch.input.value = query;
    window.aiSearch.fetchSuggestions(query);
});
```

---

## Credits & License

**Developed by**: Packaxis Development Team  
**Version**: 1.0.0  
**Last Updated**: January 2026  
**License**: Proprietary - Packaxis Packaging Canada

---

## Support

For technical support or feature requests:
- **Documentation**: [Full Docs](./AI_SEARCH_DOCUMENTATION.md)
- **GitHub Issues**: [Submit Issue](https://github.com/packaxis/packaxis-web/issues)
- **Email**: dev@packaxis.ca

---

## Changelog

### v1.0.0 (January 2026)
- ✨ Initial release with AI-powered autocomplete
- ✨ Real-time product and category suggestions
- ✨ Keyboard navigation support
- ✨ Recent search history
- ✨ Responsive mobile design
- ✨ Accessibility features (ARIA, keyboard)
- ✨ Smart caching and debouncing
- ✨ Premium UI matching design system
