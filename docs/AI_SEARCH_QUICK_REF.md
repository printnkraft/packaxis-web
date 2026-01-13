# AI Search Quick Reference

## 🚀 Quick Start

### Basic Usage (Auto-initialized in navbar)
The search is already working! Just type in the navbar search bar.

### Use on Other Pages
Add to any input:
```html
<input type="search" data-ai-search placeholder="Search...">
```

---

## ⚙️ Configuration

```javascript
new AISearch(inputElement, {
    minChars: 2,              // Min characters to trigger
    debounceTime: 300,        // Delay before API call (ms)
    maxResults: 8,            // Results per section
    showCategories: true,     // Show category matches
    showRecentSearches: true  // Show search history
});
```

---

## 🎯 API Endpoint

**GET** `/api/products/autocomplete/?q={query}&max={limit}`

**Response:**
```json
{
  "products": [{id, name, url, price, category, image_url, in_stock, sku}],
  "categories": [{id, name, slug, url, product_count}],
  "suggestions": [{text, reason}],
  "total_count": 156
}
```

---

## 🎨 Key CSS Classes

- `.ai-search-results` - Dropdown container
- `.ai-search-section` - Section wrapper (Products, Categories, etc.)
- `.ai-search-item` - Individual result item
- `.ai-search-item-image` - Product thumbnail
- `.ai-badge-success` / `.ai-badge-danger` - Stock badges

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| ↓ | Next result |
| ↑ | Previous result |
| Enter | Select / Search |
| Escape | Close dropdown |

---

## 🔧 Methods

```javascript
window.aiSearch.clear()      // Clear input & results
window.aiSearch.destroy()    // Remove component
window.aiSearch.showResults() // Show dropdown
window.aiSearch.hideResults() // Hide dropdown
```

---

## 🐛 Troubleshooting

**No autocomplete?**  
→ Check console, verify API endpoint, rebuild frontend: `npm run build`

**Images not loading?**  
→ Check `MEDIA_URL` in settings, add placeholder fallback

**Styling broken?**  
→ Clear cache (Ctrl+Shift+R), verify Vite build

---

## 📁 Files Modified

- `frontend/static/js/ai-search.js` ← Main component
- `frontend/static/css/styles.css` ← Autocomplete styles
- `frontend/templates/base.html` ← Script include
- `backend/apps/products/views.py` ← API endpoint
- `backend/apps/products/urls.py` ← Route config

---

## 🎉 Features

✅ Real-time autocomplete  
✅ Product images & prices  
✅ Category suggestions  
✅ AI-powered keywords  
✅ Recent search history  
✅ Keyboard navigation  
✅ Mobile responsive  
✅ Accessibility (ARIA)  
✅ Smart caching  
✅ Debounced input  

---

**Full Documentation**: [AI_SEARCH_DOCUMENTATION.md](./AI_SEARCH_DOCUMENTATION.md)
