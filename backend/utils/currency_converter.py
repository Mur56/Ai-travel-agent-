from __future__ import annotations

import time
from typing import Dict, Optional

import requests


class CurrencyConverter:
    """Lightweight wrapper around the ExchangeRate API with simple caching."""

    BASE_ENDPOINT = "https://v6.exchangerate-api.com/v6/{api_key}/latest/{base}"
    CACHE_TTL_SECONDS = 3600  # one hour cache per base currency

    def __init__(self, api_key: Optional[str]):
        self._api_key = api_key
        self._cache: Dict[str, Dict[str, object]] = {}

    def is_enabled(self) -> bool:
        return bool(self._api_key)

    def _fetch_rates(self, base_currency: str) -> Optional[Dict[str, float]]:
        if not self._api_key:
            return None
        base = base_currency.upper()
        cached = self._cache.get(base)
        now = time.time()
        if cached and now - cached.get("timestamp", 0) < self.CACHE_TTL_SECONDS:
            return cached.get("rates")  # type: ignore[return-value]

        url = self.BASE_ENDPOINT.format(api_key=self._api_key, base=base)
        try:
            response = requests.get(url, timeout=8)
            response.raise_for_status()
            payload = response.json()
            rates = payload.get("conversion_rates")
            if isinstance(rates, dict):
                self._cache[base] = {"rates": rates, "timestamp": now}
                return rates  # type: ignore[return-value]
        except requests.RequestException:
            return cached.get("rates") if cached else None  # type: ignore[return-value]
        return None

    def get_rate(self, from_currency: str, to_currency: str) -> Optional[float]:
        rates = self._fetch_rates(from_currency)
        if not rates:
            return None
        return rates.get(to_currency.upper())  # type: ignore[return-value]

    def convert(self, amount: float, from_currency: str, to_currency: str) -> Optional[float]:
        """Convert the amount from one currency to another."""
        rate = self.get_rate(from_currency, to_currency)
        if rate is None:
            return None
        return amount * rate