from __future__ import annotations

from typing import Dict, Optional

CURRENCY_DATA: Dict[str, Dict[str, str]] = {
    "USD": {"symbol": "$", "name": "US Dollar"},
    "EUR": {"symbol": "€", "name": "Euro"},
    "GBP": {"symbol": "£", "name": "British Pound"},
    "AUD": {"symbol": "A$", "name": "Australian Dollar"},
    "CAD": {"symbol": "C$", "name": "Canadian Dollar"},
    "NZD": {"symbol": "NZ$", "name": "New Zealand Dollar"},
    "SGD": {"symbol": "S$", "name": "Singapore Dollar"},
    "JPY": {"symbol": "¥", "name": "Japanese Yen"},
    "CNY": {"symbol": "¥", "name": "Chinese Yuan"},
    "HKD": {"symbol": "HK$", "name": "Hong Kong Dollar"},
    "TWD": {"symbol": "NT$", "name": "New Taiwan Dollar"},
    "KRW": {"symbol": "₩", "name": "South Korean Won"},
    "INR": {"symbol": "₹", "name": "Indian Rupee"},
    "AED": {"symbol": "د.إ", "name": "UAE Dirham"},
    "SAR": {"symbol": "﷼", "name": "Saudi Riyal"},
    "QAR": {"symbol": "ر.ق", "name": "Qatari Riyal"},
    "BHD": {"symbol": "ب.د", "name": "Bahraini Dinar"},
    "KWD": {"symbol": "د.ك", "name": "Kuwaiti Dinar"},
    "OMR": {"symbol": "ر.ع.", "name": "Omani Rial"},
    "ZAR": {"symbol": "R", "name": "South African Rand"},
    "BRL": {"symbol": "R$", "name": "Brazilian Real"},
    "MXN": {"symbol": "MX$", "name": "Mexican Peso"},
    "ARS": {"symbol": "AR$", "name": "Argentine Peso"},
    "CLP": {"symbol": "CLP$", "name": "Chilean Peso"},
    "COP": {"symbol": "COL$", "name": "Colombian Peso"},
    "PEN": {"symbol": "S/", "name": "Peruvian Sol"},
    "CHF": {"symbol": "CHF", "name": "Swiss Franc"},
    "SEK": {"symbol": "kr", "name": "Swedish Krona"},
    "NOK": {"symbol": "kr", "name": "Norwegian Krone"},
    "DKK": {"symbol": "kr", "name": "Danish Krone"},
    "PLN": {"symbol": "zł", "name": "Polish Złoty"},
    "CZK": {"symbol": "Kč", "name": "Czech Koruna"},
    "HUF": {"symbol": "Ft", "name": "Hungarian Forint"},
    "TRY": {"symbol": "₺", "name": "Turkish Lira"},
    "THB": {"symbol": "฿", "name": "Thai Baht"},
    "MYR": {"symbol": "RM", "name": "Malaysian Ringgit"},
    "IDR": {"symbol": "Rp", "name": "Indonesian Rupiah"},
    "VND": {"symbol": "₫", "name": "Vietnamese Dong"},
    "PHP": {"symbol": "₱", "name": "Philippine Peso"},
}

COUNTRY_TO_CURRENCY: Dict[str, str] = {
    "US": "USD",
    "CA": "CAD",
    "GB": "GBP",
    "FR": "EUR",
    "DE": "EUR",
    "ES": "EUR",
    "IT": "EUR",
    "PT": "EUR",
    "NL": "EUR",
    "BE": "EUR",
    "CH": "CHF",
    "AT": "EUR",
    "IE": "EUR",
    "SE": "SEK",
    "NO": "NOK",
    "DK": "DKK",
    "PL": "PLN",
    "CZ": "CZK",
    "HU": "HUF",
    "TR": "TRY",
    "AE": "AED",
    "SA": "SAR",
    "QA": "QAR",
    "KW": "KWD",
    "BH": "BHD",
    "OM": "OMR",
    "IN": "INR",
    "SG": "SGD",
    "MY": "MYR",
    "TH": "THB",
    "ID": "IDR",
    "VN": "VND",
    "PH": "PHP",
    "CN": "CNY",
    "JP": "JPY",
    "KR": "KRW",
    "HK": "HKD",
    "TW": "TWD",
    "AU": "AUD",
    "NZ": "NZD",
    "ZA": "ZAR",
    "BR": "BRL",
    "MX": "MXN",
    "AR": "ARS",
    "CL": "CLP",
    "CO": "COP",
    "PE": "PEN",
}

CURRENCY_KEYWORDS: Dict[str, str] = {
    "usd": "USD",
    "dollar": "USD",
    "dollars": "USD",
    "$": "USD",
    "eur": "EUR",
    "euro": "EUR",
    "euros": "EUR",
    "€": "EUR",
    "gbp": "GBP",
    "pound": "GBP",
    "pounds": "GBP",
    "£": "GBP",
    "aed": "AED",
    "dirham": "AED",
    "dirhams": "AED",
    "dhs": "AED",
    "د.إ": "AED",
    "inr": "INR",
    "rupee": "INR",
    "rupees": "INR",
    "₹": "INR",
    "yen": "JPY",
    "jpy": "JPY",
    "¥": "JPY",
    "cny": "CNY",
    "rmb": "CNY",
    "yuan": "CNY",
    "hkd": "HKD",
    "sgd": "SGD",
    "s$": "SGD",
    "cad": "CAD",
    "c$": "CAD",
    "aud": "AUD",
    "a$": "AUD",
    "nzd": "NZD",
    "chf": "CHF",
    "sar": "SAR",
    "qar": "QAR",
    "bhd": "BHD",
    "kwd": "KWD",
    "omr": "OMR",
    "zar": "ZAR",
    "rand": "ZAR",
    "brl": "BRL",
    "real": "BRL",
    "mxn": "MXN",
    "peso": "MXN",
    "mx$": "MXN",
    "php": "PHP",
    "₱": "PHP",
    "thb": "THB",
    "baht": "THB",
    "myr": "MYR",
    "ringgit": "MYR",
    "idr": "IDR",
    "rupiah": "IDR",
    "vnd": "VND",
    "dong": "VND",
}


def currency_for_country(country_code: Optional[str]) -> Optional[Dict[str, str]]:
    if not country_code:
        return None
    code = COUNTRY_TO_CURRENCY.get(country_code.upper())
    if not code:
        return None
    return currency_for_code(code)


def currency_for_code(code: Optional[str]) -> Optional[Dict[str, str]]:
    if not code:
        return None
    upper = code.upper()
    meta = CURRENCY_DATA.get(upper)
    if not meta:
        return {"code": upper, "symbol": upper + " ", "name": upper}
    return {"code": upper, **meta}


def currency_symbol(code: Optional[str]) -> str:
    if not code:
        return ""
    meta = CURRENCY_DATA.get(code.upper())
    return meta.get("symbol") if meta else code.upper() + " "


def detect_currency_in_text(text: Optional[str]) -> Optional[str]:
    if not text:
        return None
    lowered = text.lower()
    for keyword, code in CURRENCY_KEYWORDS.items():
        if keyword in lowered:
            return code
    return None