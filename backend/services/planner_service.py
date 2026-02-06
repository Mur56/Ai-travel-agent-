from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import re

from langchain_core.messages import HumanMessage

from agent.agentic_workflow import GraphBuilder
from schemas.travel import (
    BudgetGuardInsight,
    GalleryImage,
    LocaleBrief,
    LayerPreferences,
    LocalHostProfile,
    PlanSection,
    RouteMap,
    RouteNode,
    SustainabilityInsight,
    TravelPlanResponse,
    WeatherBlock,
    WeatherSnapshot,
    WellnessSyncInsight,
)
from services.plan_formatter import PlanFormatter
from utils.currency_converter import CurrencyConverter
from utils.currency_lookup import (
    currency_for_code,
    currency_for_country,
    currency_symbol,
    detect_currency_in_text,
)
from utils.location_resolver import GeoapifyLocationResolver
from utils.unsplash_client import UnsplashImageClient
from utils.weather_info import WeatherForecastTool

WORD_NUMBER_MAP = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}

HOST_ARCHETYPES = [
    {
        "name": "Aya Nakamura",
        "role": "Culinary curator",
        "specialty": "Chef tables & tasting counters",
        "availability": "Afternoons + late nights",
        "contact": "Signal · replies <2h",
    },
    {
        "name": "Mateo Ruiz",
        "role": "Nightlife fixer",
        "specialty": "Listening bars & speakeasies",
        "availability": "Thu–Sun evenings",
        "contact": "Telegram concierge channel",
    },
    {
        "name": "Lina Sørensen",
        "role": "Wellness guide",
        "specialty": "Cold plunges & forest bathing",
        "availability": "Mornings",
        "contact": "WhatsApp · pre-book 24h",
    },
    {
        "name": "Rajiv Bhatia",
        "role": "Logistics chief",
        "specialty": "Rail seats & EV fleets",
        "availability": "Daily, 08:00–22:00",
        "contact": "Shared Notion board",
    },
    {
        "name": "Chiara Venturi",
        "role": "Culture producer",
        "specialty": "Gallery unlocks & ateliers",
        "availability": "Wed–Sun",
        "contact": "Email intro via concierge",
    },
]

CALM_KEYWORDS = ["spa", "thermal", "breathe", "meditation", "soak", "massage", "wellness", "slow"]
INTENSE_KEYWORDS = ["hike", "trek", "ski", "summit", "cycle", "climb", "surf", "trail"]

SYMBOL_TO_CURRENCY = {
    "$": "USD",
    "€": "EUR",
    "£": "GBP",
    "₹": "INR",
    "¥": "JPY",
    "₩": "KRW",
    "₺": "TRY",
    "₱": "PHP",
    "₫": "VND",
    "ر.ق": "QAR",
    "﷼": "SAR",
    "د.إ": "AED",
    "د.ك": "KWD",
    "ب.د": "BHD",
    "ر.ع.": "OMR",
    "R$": "BRL",
    "S$": "SGD",
    "C$": "CAD",
    "A$": "AUD",
    "HK$": "HKD",
    "MX$": "MXN",
    "R": "ZAR",
}

BUDGET_KEYWORDS = (
    "budget",
    "under",
    "around",
    "about",
    "cap",
    "limit",
    "spend",
    "cost",
    "allocate",
    "set aside",
    "max",
)

DEFAULT_CURRENCY = "USD"


class PlannerServiceError(Exception):
    """Raised when the planner service cannot fulfill a request."""


class PlannerService:
    def __init__(self):
        self._graph = None
        self._model_provider = os.environ.get("MODEL_PROVIDER", "groq")
        self._graph_builder = GraphBuilder(model_provider=self._model_provider)
        api_key = os.environ.get("OPENWEATHERMAP_API_KEY")
        self._weather_tool = WeatherForecastTool(api_key) if api_key else None
        self._location_resolver = GeoapifyLocationResolver()
        self._image_client = UnsplashImageClient()
        exchange_key = os.environ.get("EXCHANGE_RATE_API_KEY")
        self._currency_converter = CurrencyConverter(exchange_key) if exchange_key else None

    def warmup(self) -> None:
        """Eagerly build the LangGraph so the first request is fast."""
        self._ensure_graph()

    def _ensure_graph(self) -> None:
        if self._graph is None:
            self._graph = self._graph_builder()

    def _invoke_agent(self, query: str) -> str:
        self._ensure_graph()
        try:
            input_state = {"messages": [HumanMessage(content=query)]}
            output = self._graph.invoke(input_state)
            if isinstance(output, dict) and "messages" in output:
                return output["messages"][-1].content
            return str(output)
        except Exception as exc:  # pragma: no cover - relies on remote LLM
            raise PlannerServiceError("Failed to generate itinerary from the agent") from exc

    def _build_weather_block(self, location: Optional[str]) -> Optional[WeatherBlock]:
        if not location or not self._weather_tool:
            return None
        try:
            current = self._weather_tool.get_current_weather(location)
            forecast = self._weather_tool.get_forecast_weather(location)
        except Exception:
            return None

        if not current:
            return None

        current_main = current.get("main", {})
        current_temp = current_main.get("temp")
        humidity = current_main.get("humidity")
        wind_speed = current.get("wind", {}).get("speed")
        condition = (current.get("weather") or [{}])[0].get("description")

        forecast_entries = forecast.get("list", []) if isinstance(forecast, dict) else []
        snapshots: List[WeatherSnapshot] = []
        temps: List[float] = []
        rain_chance = None

        for entry in forecast_entries[:6]:
            entry_main = entry.get("main", {})
            temp = entry_main.get("temp")
            if isinstance(temp, (int, float)):
                temps.append(temp)
            pop = entry.get("pop")
            if pop is not None and rain_chance is None:
                rain_chance = int(round(pop * 100))
            snapshots.append(
                WeatherSnapshot(
                    label=entry.get("dt_txt", "Soon"),
                    tempC=temp,
                    description=(entry.get("weather") or [{}])[0].get("description"),
                    rainChance=int(round(pop * 100)) if isinstance(pop, (int, float)) else None,
                )
            )

        temps_source = temps + ([current_temp] if isinstance(current_temp, (int, float)) else [])
        high = max(temps_source) if temps_source else None
        low = min(temps_source) if temps_source else None

        sunrise = current.get("sys", {}).get("sunrise")
        sunset = current.get("sys", {}).get("sunset")
        daylight = None
        if isinstance(sunrise, int) and isinstance(sunset, int) and sunset > sunrise:
            duration = sunset - sunrise
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            daylight = f"{hours}h {minutes:02d}m"

        trend = None
        if snapshots and isinstance(current_temp, (int, float)) and isinstance(snapshots[0].tempC, (int, float)):
            delta = snapshots[0].tempC - current_temp
            if abs(delta) >= 1:
                sign = "+" if delta > 0 else ""
                trend = f"{sign}{round(delta)}°C vs now"

        wind_kph = round(wind_speed * 3.6, 1) if isinstance(wind_speed, (int, float)) else None

        return WeatherBlock(
            location=location,
            summary="Live feed via OpenWeather",
            high=high,
            low=low,
            condition=condition,
            humidity=humidity,
            windKph=wind_kph,
            daylight=daylight,
            trend=trend,
            rainChance=rain_chance,
            forecast=snapshots,
        )

    def _build_route_map(self, labels: List[str]) -> Optional[RouteMap]:
        if not labels:
            return None
        resolved_points = self._location_resolver.resolve_many(labels[:6])
        if not resolved_points:
            return None

        nodes = [
            RouteNode(
                label=point.get("display_name") or point.get("label"),
                latitude=point["latitude"],
                longitude=point["longitude"],
                hint=point.get("label"),
            )
            for point in resolved_points
            if point.get("latitude") is not None and point.get("longitude") is not None
        ]

        if not nodes:
            return None
        return RouteMap(nodes=nodes)

    def _infer_party_size(self, prompt: str) -> int:
        if not prompt:
            return 2
        prompt_lower = prompt.lower()
        if "solo" in prompt_lower:
            return 1
        if any(term in prompt_lower for term in ("honeymoon", "couple", "duo")):
            return 2
        if "family" in prompt_lower:
            if "four" in prompt_lower:
                return 4
            if "five" in prompt_lower:
                return 5
        digit_match = re.search(r"(party|group|family|for)\s+of\s+(\d+)", prompt_lower)
        if digit_match:
            try:
                return max(1, min(10, int(digit_match.group(2))))
            except ValueError:
                pass
        word_match = re.search(r"(party|group|family|for)\s+of\s+(one|two|three|four|five|six|seven|eight|nine|ten)", prompt_lower)
        if word_match:
            return WORD_NUMBER_MAP.get(word_match.group(2), 2)
        explicit_digit = re.search(r"(\d+)\s*(traveler|traveller|people|guests|pax)", prompt_lower)
        if explicit_digit:
            try:
                return max(1, min(12, int(explicit_digit.group(1))))
            except ValueError:
                pass
        return 2

    def _build_budget_guard(
        self,
        sections: List[PlanSection],
        prompt: str,
        location: Optional[str],
        party_size: int,
        user_currency: str,
        location_currency: Optional[Dict[str, str]],
        explicit_budget: Optional[Dict[str, object]],
    ) -> BudgetGuardInsight:
        nights = max(len(sections), 1)
        base_currency = (user_currency or DEFAULT_CURRENCY).upper()
        prompt_lower = prompt.lower()

        if explicit_budget:
            raw_amount = float(explicit_budget.get("amount", 0))
            per_person_value = raw_amount if explicit_budget.get("per_person") else raw_amount / max(party_size, 1)
            tier = "Custom spend"
            low_total = per_person_value * party_size * 0.95
            high_total = per_person_value * party_size * 1.05
            risk_alerts = ["Anchored to provided budget"]
        else:
            base_rate = 280
            if any(keyword in prompt_lower for keyword in ("luxury", "five-star", "palace", "ultra")):
                base_rate += 140
            if "budget" in prompt_lower or "value" in prompt_lower:
                base_rate -= 60
            base_rate = max(140, base_rate)
            per_person_value = base_rate * nights
            total_value = per_person_value * party_size
            low_total = total_value * 0.9
            high_total = total_value * 1.2
            tier = "Boutique+" if base_rate >= 320 else "Premium"
            if base_rate > 420:
                tier = "Ultra Lux"
            risk_alerts = []
            if nights >= 6:
                risk_alerts.append("Long arc – pad buffer nights for drift")
            if "multiple" in prompt_lower or "multi-city" in prompt_lower:
                risk_alerts.append("Stacked routes – confirm transfer holds")
            if not risk_alerts:
                risk_alerts.append("Track dining prepayments to avoid duplicate holds")

        total_range = f"{self._format_money(low_total, base_currency)} – {self._format_money(high_total, base_currency)}"
        per_person_str = self._format_money(per_person_value, base_currency)

        location_hint = location or "destination"
        recommended_splits = [
            f"60% stays · {location_hint}",
            "25% dining & tastings",
            "15% experiences + logistics",
        ]

        local_range = None
        per_person_local = None
        conversion_rate = None
        local_currency_code = location_currency.get("code") if location_currency else None
        if local_currency_code:
            conversion_rate = self._get_conversion_rate(base_currency, local_currency_code)
            if conversion_rate:
                per_person_local_value = per_person_value * conversion_rate
                low_total_local = low_total * conversion_rate
                high_total_local = high_total * conversion_rate
                per_person_local = self._format_money(per_person_local_value, local_currency_code)
                local_range = f"{self._format_money(low_total_local, local_currency_code)} – {self._format_money(high_total_local, local_currency_code)}"

        return BudgetGuardInsight(
            tier=tier,
            perPerson=per_person_str,
            totalRange=total_range,
            riskAlerts=risk_alerts,
            recommendedSplits=recommended_splits,
            currencyCode=base_currency,
            currencySymbol=currency_symbol(base_currency),
            localCurrencyCode=local_currency_code,
            localCurrencySymbol=currency_symbol(local_currency_code),
            perPersonLocal=per_person_local,
            localRange=local_range,
            conversionRate=conversion_rate,
        )

    def _build_local_hosts(self, location: Optional[str]) -> List[LocalHostProfile]:
        if not location:
            location = "Destination"
        base_index = abs(hash(location))
        profiles: List[LocalHostProfile] = []
        for offset in range(3):
            template = HOST_ARCHETYPES[(base_index + offset) % len(HOST_ARCHETYPES)]
            profiles.append(
                LocalHostProfile(
                    name=template["name"],
                    role=template["role"],
                    specialty=f"{template['specialty']} · {location}",
                    contactHint=template["contact"],
                    availability=template["availability"],
                )
            )
        return profiles

    def _build_wellness_sync(self, sections: List[PlanSection]) -> WellnessSyncInsight:
        calm_hits = 0
        intense_hits = 0
        anchors: List[str] = []
        for section in sections:
            for detail in section.details:
                text = detail.lower()
                if any(keyword in text for keyword in CALM_KEYWORDS):
                    calm_hits += 1
                    anchors.append(detail)
                if any(keyword in text for keyword in INTENSE_KEYWORDS):
                    intense_hits += 1
            if len(anchors) >= 3:
                break
        raw_score = 70 + (calm_hits * 4) - (intense_hits * 3)
        balance_score = max(45, min(95, raw_score))
        tempo = "Balanced recovery"
        if balance_score < 60:
            tempo = "High tempo – add recovery"
        elif balance_score > 85:
            tempo = "Ultra restorative"
        recommendations = []
        if balance_score < 65:
            recommendations.append("Inject morning breath-work or gentle mobility after transit days")
        else:
            recommendations.append("Maintain hydration + light protein to sustain the pace")
        if intense_hits > calm_hits:
            recommendations.append("Lock spa or float session mid-journey")
        else:
            recommendations.append("Keep circadian rhythm by anchoring wake windows")
        if not anchors:
            anchors = ["Sunrise stretch + hydration cadence"]
        return WellnessSyncInsight(
            balanceScore=balance_score,
            tempo=tempo,
            anchors=anchors[:3],
            recommendations=recommendations,
        )

    def _build_sustainability(self, route_labels: List[str]) -> SustainabilityInsight:
        if not route_labels:
            route_labels = ["Itinerary"]
        low_impact_moves: List[str] = []
        for idx in range(len(route_labels) - 1):
            origin = route_labels[idx]
            target = route_labels[idx + 1]
            low_impact_moves.append(f"Use high-speed rail between {origin} → {target} with door-to-door transfers")
        if not low_impact_moves:
            low_impact_moves.append("Prioritize walking loops + micro-mobility in core districts")
        energy_notes = [
            "Bias boutique hotels with renewable sourcing",
            "Bundle dining to suppliers with traceable sourcing",
        ]
        status = "On track"
        if len(route_labels) >= 4:
            status = "Monitor"  # more hops = harder to stay green
        return SustainabilityInsight(
            co2Delta="-28% vs flights",
            lowImpactMoves=low_impact_moves,
            energyNotes=energy_notes,
            status=status,
        )

    def _currency_from_symbol(self, symbol: Optional[str]) -> Optional[str]:
        if not symbol:
            return None
        return SYMBOL_TO_CURRENCY.get(symbol.strip())

    def _normalize_amount(self, raw_value: str) -> Optional[float]:
        token = raw_value.replace(",", "").strip().lower()
        multiplier = 1.0
        for suffix, factor in (("b", 1_000_000_000), ("m", 1_000_000), ("k", 1_000)):
            if token.endswith(suffix):
                multiplier = factor
                token = token[:-1]
                break
        try:
            return float(token) * multiplier
        except ValueError:
            return None

    def _extract_budget_from_prompt(self, prompt: str) -> Optional[Dict[str, object]]:
        if not prompt:
            return None
        lowered = prompt.lower()
        snippets = []
        for keyword in BUDGET_KEYWORDS:
            idx = lowered.find(keyword)
            if idx != -1:
                start = max(0, idx - 12)
                end = min(len(prompt), idx + 80)
                snippets.append(prompt[start:end])
        if not snippets:
            snippets = [prompt]

        symbol_pattern = re.compile(
            r"(?P<symbol>(?:د\.إ|ر\.ق|﷼|د\.ك|ب\.د|ر\.ع\.|[$€£₹¥₩₺₱₫]|A\$|C\$|S\$|HK\$|MX\$|R\$))\s*(?P<amount>\d[\d,]*(?:\.\d+)?(?:\s?[kKmMbB])?)"
        )
        code_pattern = re.compile(r"(?P<amount>\d[\d,]*(?:\.\d+)?(?:\s?[kKmMbB])?)\s*(?P<code>(usd|eur|gbp|aed|inr|jpy|cny|hkd|sgd|cad|aud|nzd|chf|sar|qar|bhd|kwd|zar|brl|mxn|thb|myr|idr|vnd|php|try))", re.IGNORECASE)

        for snippet in snippets:
            symbol_match = symbol_pattern.search(snippet)
            code_match = code_pattern.search(snippet)
            amount_token = None
            currency_code = None
            if symbol_match:
                amount_token = symbol_match.group("amount")
                currency_code = self._currency_from_symbol(symbol_match.group("symbol"))
            elif code_match:
                amount_token = code_match.group("amount")
                matched_code = code_match.group("code")
                if matched_code:
                    meta = currency_for_code(matched_code.upper())
                    currency_code = meta["code"] if meta else matched_code.upper()
            if amount_token:
                amount_value = self._normalize_amount(amount_token)
                if amount_value:
                    per_person = bool(re.search(r"per\s+(?:person|guest|traveler|traveller|head)|\bpp\b", snippet, re.IGNORECASE))
                    return {
                        "amount": amount_value,
                        "currency": currency_code,
                        "per_person": per_person,
                    }
        return None

    def _detect_user_currency(self, prompt: str) -> str:
        detected = detect_currency_in_text(prompt)
        if detected:
            return detected
        return DEFAULT_CURRENCY

    def _format_money(self, amount: float, currency_code: str) -> str:
        symbol = currency_symbol(currency_code) or currency_code + " "
        if abs(amount) >= 1000:
            formatted = f"{amount:,.0f}"
        elif abs(amount) >= 100:
            formatted = f"{amount:,.2f}"
        else:
            formatted = f"{amount:,.2f}"
        return f"{symbol}{formatted}"

    def _convert_amount(self, amount: float, from_currency: str, to_currency: str) -> Optional[float]:
        if not self._currency_converter or not self._currency_converter.is_enabled():
            return None
        if from_currency.upper() == to_currency.upper():
            return amount
        return self._currency_converter.convert(amount, from_currency.upper(), to_currency.upper())

    def _get_conversion_rate(self, from_currency: str, to_currency: str) -> Optional[float]:
        if not self._currency_converter or not self._currency_converter.is_enabled():
            return None
        return self._currency_converter.get_rate(from_currency.upper(), to_currency.upper())

    def _resolve_location_currency(self, location: Optional[str]) -> Optional[Dict[str, str]]:
        if not location:
            return None
        metadata = self._location_resolver.resolve(location)
        country_code = metadata.get("country_code") if metadata else None
        currency_meta = currency_for_country(country_code)
        return currency_meta

    def _extract_gallery_query(self, prompt: str) -> Optional[str]:
        if not prompt:
            return None
        match = re.search(r"([A-Z][a-z]+(?:\s[A-Z][a-z]+){0,2})", prompt)
        if match:
            return match.group(1)
        return None

    def _build_gallery_images(self, primary_location: Optional[str], route_labels: List[str], prompt: str) -> List[GalleryImage]:
        if not self._image_client or not self._image_client.is_enabled():
            return []

        query_candidates: List[str] = []
        if primary_location:
            query_candidates.append(primary_location)
        query_candidates.extend([label for label in route_labels if label])
        fallback_query = self._extract_gallery_query(prompt)
        if fallback_query:
            query_candidates.append(fallback_query)

        seen = set()
        for candidate in query_candidates:
            if not candidate or candidate in seen:
                continue
            seen.add(candidate)
            enriched_query = f"{candidate} travel" if "travel" not in candidate.lower() else candidate
            images = self._image_client.fetch_gallery(enriched_query, count=4)
            if images:
                return images
        return []

    def generate_plan(self, query: str, layers: Optional[LayerPreferences] = None) -> TravelPlanResponse:
        if not query.strip():
            raise PlannerServiceError("Query cannot be empty")

        layer_settings = layers or LayerPreferences()
        answer = self._invoke_agent(query)
        sections = PlanFormatter.sections_from_answer(answer)
        if not sections:
            sections = [PlanSection(title="Highlights", details=[answer])] if answer else []
        key_moments = PlanFormatter.key_moments_from_answer(answer)
        locale_brief_data = PlanFormatter.locale_brief_from_answer(answer)
        locale_brief = LocaleBrief(**locale_brief_data) if locale_brief_data else None
        route_labels = PlanFormatter.extract_route_labels(sections, query)

        weather_block = self._build_weather_block(route_labels[0] if route_labels else None) if layer_settings.liveWeather else None
        route_map = self._build_route_map(route_labels) if layer_settings.mapLayers else None
        primary_location = route_labels[0] if route_labels else None
        location_currency = self._resolve_location_currency(primary_location)
        party_size = self._infer_party_size(query)
        explicit_budget = self._extract_budget_from_prompt(query)
        user_currency = (
            (explicit_budget.get("currency") if explicit_budget and explicit_budget.get("currency") else None)
            or self._detect_user_currency(query)
        )
        if explicit_budget and not explicit_budget.get("currency"):
            explicit_budget["currency"] = user_currency
        budget_guard = (
            self._build_budget_guard(
                sections,
                query,
                primary_location,
                party_size,
                user_currency,
                location_currency,
                explicit_budget,
            )
            if layer_settings.budgetGuard
            else None
        )
        local_hosts = self._build_local_hosts(primary_location) if layer_settings.localHosts else []
        wellness_sync = self._build_wellness_sync(sections) if layer_settings.wellnessSync else None
        sustainability = (
            self._build_sustainability(route_labels or ([primary_location] if primary_location else []))
            if layer_settings.sustainMode
            else None
        )
        gallery_images = self._build_gallery_images(primary_location, route_labels, query)

        timestamp = datetime.now(timezone.utc).isoformat()

        return TravelPlanResponse(
            answer=answer,
            itinerary=sections,
            keyMoments=key_moments,
            localeBrief=locale_brief,
            weather=weather_block,
            routeMap=route_map,
            budgetGuard=budget_guard,
            localHosts=local_hosts,
            wellnessSync=wellness_sync,
            sustainability=sustainability,
            galleryImages=gallery_images,
            layers=layer_settings,
            timestamp=timestamp,
        )


planner_service = PlannerService()