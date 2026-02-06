from __future__ import annotations

import os
from typing import List, Optional

import requests

from schemas.travel import GalleryImage


class UnsplashImageClient:
    """Thin wrapper around the Unsplash Search API for curated gallery pulls."""

    BASE_URL = "https://api.unsplash.com/search/photos"

    def __init__(self, access_key: Optional[str] = None):
        self._access_key = access_key or os.environ.get("UNSPLASH_ACCESS_KEY")
        self._session = requests.Session()

    def is_enabled(self) -> bool:
        return bool(self._access_key)

    def fetch_gallery(self, query: Optional[str], count: int = 3) -> List[GalleryImage]:
        if not self.is_enabled() or not query:
            return []

        params = {
            "query": query,
            "per_page": max(1, min(10, count)),
            "orientation": "landscape",
            "content_filter": "high",
        }
        headers = {"Authorization": f"Client-ID {self._access_key}"}

        try:
            response = self._session.get(self.BASE_URL, params=params, headers=headers, timeout=6)
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException:
            return []

        results = payload.get("results", []) if isinstance(payload, dict) else []
        gallery: List[GalleryImage] = []

        for item in results:
            urls = item.get("urls") or {}
            url = urls.get("regular") or urls.get("full") or urls.get("small")
            if not url:
                continue
            alt = item.get("alt_description") or item.get("description")
            photographer = (item.get("user") or {}).get("name")
            gallery.append(
                GalleryImage(
                    url=url,
                    alt=alt,
                    photographer=photographer,
                    source="Unsplash",
                )
            )
            if len(gallery) >= count:
                break

        return gallery