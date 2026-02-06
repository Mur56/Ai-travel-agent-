from __future__ import annotations

import re
from typing import List, Optional, Tuple

from schemas.travel import PlanSection


class PlanFormatter:
    """Utility helpers to normalize LLM text into structured sections and highlights."""

    DAY_PATTERN = re.compile(r"^(day\s*\d+[^:]*):?\s*(.*)$", re.IGNORECASE)
    HEADER_PATTERN = re.compile(
        r"^(morning|afternoon|evening|night|highlight|stay|dining|experience)s?:?",
        re.IGNORECASE
    )
    BULLET_PATTERN = re.compile(r"^[-•]\s*(.+)$")
    LOCATION_FROM_TITLE = re.compile(r"day\s*\d+\s*[\-:–]\s*(.+)$", re.IGNORECASE)
    LOCATION_INLINE = re.compile(r"in\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+){0,2})")
    CAPITALIZED_SEQUENCE = re.compile(r"([A-Z][a-z]+(?:\s[A-Z][a-z]+){0,2})")
    STOPWORDS = {
        "Design",
        "Plan",
        "Craft",
        "Trip",
        "Travel",
        "Day",
        "Morning",
        "Afternoon",
        "Evening",
    }
    SECTION_STOP_PREFIXES = (
        "locale brief",
        "key moments",
        "budget guard",
        "budget",
        "local hosts",
        "wellness",
        "sustainability",
        "route",
        "gallery",
        "weather",
        "itinerary",
        "daily plan",
        "operations",
    )

    SectionLine = Tuple[str, bool]

    @classmethod
    def _normalize_lines(cls, answer: str) -> List[str]:
        if not answer:
            return []
        return [
            line.strip().strip("•-")
            for line in answer.splitlines()
            if line.strip()
        ]

    @classmethod
    def _extract_section_block(
        cls,
        answer: str,
        anchors: Tuple[str, ...]
    ) -> List[Tuple[str, bool]]:
        lines = answer.splitlines()
        block: List[Tuple[str, bool]] = []
        capturing = False

        for raw in lines:
            stripped = raw.strip()
            if not stripped:
                if capturing and block:
                    continue
                continue

            normalized = stripped.lower().rstrip(":")
            if not capturing and any(
                normalized.startswith(anchor) for anchor in anchors
            ):
                capturing = True
                block = []
                continue

            if capturing:
                stop_hit = any(
                    normalized.startswith(stop)
                    for stop in cls.SECTION_STOP_PREFIXES
                )
                if (
                    cls.DAY_PATTERN.match(stripped)
                    or cls.HEADER_PATTERN.match(stripped)
                    or stop_hit
                ):
                    if (
                        stop_hit
                        and any(
                            normalized.startswith(anchor)
                            for anchor in anchors
                        )
                        and not block
                    ):
                        continue  # ignore repeated section heading before content
                    break

                is_bullet = bool(re.match(r"^[-•*]", stripped))
                clean = re.sub(r"^[-•*]\s*", "", stripped).strip()
                if clean:
                    block.append((clean, is_bullet))

        return block

    @classmethod
    def sections_from_answer(cls, answer: str) -> List[PlanSection]:
        lines = cls._normalize_lines(answer)
        if not lines:
            return []

        sections: List[PlanSection] = []
        current_title = None
        current_details: List[str] = []
        skip_block = False

        for line in lines:
            stripped_lead = re.sub(
                r"^[*#>\-`_\s]+", "", line
            ).strip()
            lowered_heading = stripped_lead.lower()
            day_match = cls.DAY_PATTERN.match(line)

            if day_match:
                if skip_block:
                    skip_block = False
                if current_title:
                    sections.append(
                        PlanSection(
                            title=current_title,
                            details=current_details
                        )
                    )
                title = day_match.group(1).strip().replace("  ", " ")
                detail = day_match.group(2).strip()
                current_title = title
                current_details = [detail] if detail else []
                continue

            header_match = cls.HEADER_PATTERN.match(line)
            if header_match:
                if skip_block:
                    skip_block = False
                if current_title:
                    sections.append(
                        PlanSection(
                            title=current_title,
                            details=current_details
                        )
                    )
                header = header_match.group(1).capitalize()
                detail_text = line[
                    header_match.end():
                ].strip(" :-")
                current_title = f"{header} Focus"
                current_details = [detail_text] if detail_text else []
                continue

            if (
                lowered_heading.startswith("locale brief")
                or lowered_heading.startswith("key moments")
            ):
                skip_block = True
                continue

            if skip_block:
                continue

            if current_title is None:
                current_title = "Highlights"
                current_details = []

            current_details.append(line)

        if current_title:
            sections.append(
                PlanSection(
                    title=current_title,
                    details=current_details
                )
            )

        if not sections and lines:
            sections.append(
                PlanSection(
                    title="Highlights",
                    details=lines
                )
            )

        return sections

    @classmethod
    def key_moments_from_answer(
        cls,
        answer: str,
        limit: int = 6
    ) -> List[str]:
        highlights: List[str] = []
        seen = set()

        anchored_block = cls._extract_section_block(
            answer,
            ("key moments",)
        )
        if anchored_block:
            for text, is_bullet in anchored_block:
                if not is_bullet:
                    continue
                snippet = text.strip()
                if snippet and snippet not in seen:
                    highlights.append(snippet)
                    seen.add(snippet)
                if len(highlights) >= limit:
                    break
            if highlights:
                return highlights

        raw_lines = [
            line.strip()
            for line in answer.splitlines()
            if line.strip()
        ]
        for line in raw_lines:
            bullet_match = re.match(
                r"^[-•*]\s*(.+)$",
                line
            )
            candidate = (
                bullet_match.group(1)
                if bullet_match
                else line
            )
            lowered = candidate.lower()
            if (
                bullet_match
                or any(
                    keyword in lowered
                    for keyword in (
                        "must",
                        "highlight",
                        "don't miss",
                        "don’t miss",
                        "signature",
                        "key moment",
                    )
                )
            ):
                snippet = candidate.strip()
                if snippet and snippet not in seen:
                    highlights.append(snippet)
                    seen.add(snippet)
            if len(highlights) >= limit:
                break

        return highlights

    @classmethod
    def locale_brief_from_answer(
        cls,
        answer: str
    ) -> Optional[dict]:
        block = cls._extract_section_block(
            answer,
            ("locale brief",)
        )
        if not block:
            return None

        summary_lines: List[str] = []
        highlights: List[str] = []

        for text, is_bullet in block:
            if is_bullet:
                if text not in highlights:
                    highlights.append(text)
            else:
                cleaned = re.sub(r"\s+", " ", text).strip()
                if not cleaned:
                    continue
                if (
                    len(cleaned.split()) <= 2
                    and not re.search(r"[.!?]", cleaned)
                ):
                    # Likely just a heading or city name, skip
                    continue
                summary_lines.append(cleaned)

        summary = " ".join(summary_lines).strip()
        if not summary and highlights:
            summary = highlights[0]

        if not summary:
            return None

        return {
            "summary": summary,
            "highlights": [
                item.strip()
                for item in highlights[:5]
                if item.strip()
            ],
        }

    @classmethod
    def extract_route_labels(
        cls,
        sections: List[PlanSection],
        fallback_text: str
    ) -> List[str]:
        labels: List[str] = []

        def add_label(value: str):
            clean = value.strip().strip(".,")
            if clean and clean not in labels:
                labels.append(clean)

        for section in sections:
            title_match = cls.LOCATION_FROM_TITLE.search(
                section.title
            )
            if title_match:
                add_label(title_match.group(1))
                continue

            for detail in section.details:
                inline_match = cls.LOCATION_INLINE.search(
                    detail
                )
                if inline_match:
                    add_label(inline_match.group(1))

        if not labels and fallback_text:
            for match in cls.CAPITALIZED_SEQUENCE.findall(
                fallback_text
            ):
                token = match.strip()
                if token and token not in cls.STOPWORDS:
                    add_label(token)

        return labels
