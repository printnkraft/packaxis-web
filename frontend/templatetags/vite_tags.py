from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

from django import template
from django.conf import settings

register = template.Library()


@lru_cache(maxsize=1)
def _load_manifest() -> Dict[str, Any]:
    base_dir = Path(settings.BASE_DIR)
    manifest_path = base_dir / "frontend" / "static" / "dist" / ".vite" / "manifest.json"
    if not manifest_path.exists():
        return {}
    try:
        return json.loads(manifest_path.read_text())
    except Exception:
        return {}


def _asset_url(filename: str) -> str:
    static_url = settings.STATIC_URL.rstrip("/")
    return f"{static_url}/dist/{filename}"


@register.simple_tag
def vite_js(entry: str) -> str:
    manifest = _load_manifest()
    chunk = manifest.get(entry)
    if not chunk:
        return ""
    return _asset_url(chunk.get("file", ""))


@register.simple_tag
def vite_css(entry: str) -> str:
    manifest = _load_manifest()
    chunk = manifest.get(entry)
    if not chunk:
        return ""
    css_files = chunk.get("css") or []
    if not css_files:
        return ""
    return _asset_url(css_files[0])
