"""
Vite template tags for Django integration.

Loads assets from the Vite manifest.json file and provides template tags
to include CSS and JS files with cache-busted hashes.
"""

import json
import os
from pathlib import Path

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()

# Cache the manifest in memory
_manifest = None


def load_manifest():
    """Load the Vite manifest.json file."""
    global _manifest
    
    # In DEBUG mode, always reload to pick up new builds
    if _manifest is not None and not settings.DEBUG:
        return _manifest

    manifest_path = Path(settings.BASE_DIR).parent / "frontend" / "static" / "dist" / ".vite" / "manifest.json"
    
    if not manifest_path.exists():
        if settings.DEBUG:
            # In development, return empty dict if manifest doesn't exist
            return {}
        raise FileNotFoundError(f"Vite manifest not found at {manifest_path}")
    
    with open(manifest_path, "r", encoding="utf-8") as f:
        _manifest = json.load(f)
    
    return _manifest


@register.simple_tag
def vite_css(entry, **kwargs):
    """
    Load CSS files for a Vite entry point.
    
    Usage:
        {% vite_css 'src/main.ts' as vite_main_css %}
        {% if vite_main_css %}
            <link rel="stylesheet" href="{{ vite_main_css }}" />
        {% endif %}
    """
    manifest = load_manifest()
    
    if not manifest:
        return ""
    
    entry_data = manifest.get(entry)
    if not entry_data:
        return ""
    
    css_files = entry_data.get("css", [])
    if not css_files:
        return ""
    
    # Return the first CSS file path
    css_file = css_files[0]
    return f"/static/dist/{css_file}"


@register.simple_tag
def vite_js(entry, **kwargs):
    """
    Load JS files for a Vite entry point.
    
    Usage:
        {% vite_js 'src/main.ts' as vite_main_js %}
        {% if vite_main_js %}
            <script type="module" src="{{ vite_main_js }}"></script>
        {% endif %}
    """
    manifest = load_manifest()
    
    if not manifest:
        return ""
    
    entry_data = manifest.get(entry)
    if not entry_data:
        return ""
    
    js_file = entry_data.get("file")
    if not js_file:
        return ""
    
    return f"/static/dist/{js_file}"
