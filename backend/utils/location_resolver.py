from __future__ import annotations

import os
from typing import Dict, List, Optional

import requests


class GeoapifyLocationResolver:
    """Lightweight helper to turn place names into lat/lon coordinates."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEOAPIFY_API_KEY")
        self.endpoint = "https://api.geoapify.com/v1/geocode/search"

    def resolve(self, place: str) -> Optional[Dict[str, float]]:
        if not place or not self.api_key:
            return None
        try:
            params = {"text": place, "limit": 1, "apiKey": self.api_key}
            response = requests.get(self.endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            features = data.get("features") or []
            if not features:
                return None
            feature = features[0]
            lon, lat = feature.get("geometry", {}).get("coordinates", [None, None])
            if lat is None or lon is None:
                return None
            props = feature.get("properties", {})
            return {
                "label": place,
                "display_name": props.get("formatted") or place,
                "latitude": lat,
                "longitude": lon,
                "country": props.get("country"),
                "country_code": props.get("country_code"),
            }
        except requests.RequestException:
            return None

    def resolve_many(self, places: List[str]) -> List[Dict[str, float]]:
        resolved = []
        for place in places:
            match = self.resolve(place)
            if match:
                resolved.append(match)
        return resolved