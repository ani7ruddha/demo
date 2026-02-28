"""
Cleaning / normalization module.

Converts raw extracted records into a canonical schema with:
- Parsed impression ranges → lower / upper / mid numeric values
- Parsed start_date → Python date
- Cleaned creative_text (body + headline combined)
- Normalized advertiser name
"""

from __future__ import annotations

import json
import math
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
EXTRACTED_INPUT = DATA_DIR / "ads_extracted.jsonl"
CLEAN_OUTPUT = DATA_DIR / "ads_clean.jsonl"

TODAY = date.today()

# ---------------------------------------------------------------------------
# Impression range parsing
# ---------------------------------------------------------------------------

_SUFFIXES = {"k": 1_000, "m": 1_000_000, "b": 1_000_000_000}


def _parse_number(s: str) -> float:
    """Parse '10K', '1.5M', '500', etc. → float."""
    s = s.strip().replace(",", "")
    suffix = s[-1].lower() if s and s[-1].lower() in _SUFFIXES else None
    try:
        base = float(s[:-1]) if suffix else float(s)
        return base * _SUFFIXES.get(suffix, 1)
    except ValueError:
        return 0.0


_RANGE_PATTERN = re.compile(
    r"([\d,.]+[KkMmBb]?)\s*[–\-–—]\s*([\d,.]+[KkMmBb]?)\s*impressions?",
    re.IGNORECASE,
)
_LOWER_ONLY_PATTERN = re.compile(
    r"([\d,.]+[KkMmBb]?)\+?\s*impressions?",
    re.IGNORECASE,
)


def parse_impressions(raw: str) -> tuple[float, float, float]:
    """
    Returns (lower, upper, mid).
    If only a lower bound is found, mid = lower.
    """
    if not raw:
        return (0.0, 0.0, 0.0)

    m = _RANGE_PATTERN.search(raw)
    if m:
        lower = _parse_number(m.group(1))
        upper = _parse_number(m.group(2))
        mid = (lower + upper) / 2.0
        return (lower, upper, mid)

    m = _LOWER_ONLY_PATTERN.search(raw)
    if m:
        lower = _parse_number(m.group(1))
        return (lower, lower, lower)

    return (0.0, 0.0, 0.0)


# ---------------------------------------------------------------------------
# Date parsing
# ---------------------------------------------------------------------------

_DATE_FORMATS = [
    "%B %d, %Y",   # January 15, 2024
    "%b %d, %Y",   # Jan 15, 2024
    "%Y-%m-%d",    # 2024-01-15
    "%m/%d/%Y",    # 01/15/2024
    "%d %B %Y",    # 15 January 2024
    "%d %b %Y",    # 15 Jan 2024
]


def parse_start_date(raw: str) -> date | None:
    """Try multiple date formats; return a date object or None."""
    if not raw:
        return None
    raw = raw.strip().rstrip(".")
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            pass
    # Try to parse just year if present
    m = re.search(r"\b(20\d{2})\b", raw)
    if m:
        return date(int(m.group(1)), 1, 1)
    return None


def days_running(start: date | None) -> int:
    if start is None:
        return 0
    delta = (TODAY - start).days
    return max(delta, 0)


# ---------------------------------------------------------------------------
# Text cleaning
# ---------------------------------------------------------------------------

def clean_text(text: str) -> str:
    """Basic text normalisation."""
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    return text


def build_creative_text(body: str, headline: str) -> str:
    """Combine ad body and headline into a single embedding-ready string."""
    parts = [p for p in [headline, body] if p]
    return clean_text(" | ".join(parts))


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------

def normalize(record: dict[str, Any]) -> dict[str, Any]:
    """Transform an extracted record into the canonical schema."""
    impression_raw = record.get("impression_raw", "")
    imp_lower, imp_upper, imp_mid = parse_impressions(impression_raw)

    start_date = parse_start_date(record.get("start_date_raw", ""))
    longevity_days = days_running(start_date)

    body = clean_text(record.get("ad_body", ""))
    headline = clean_text(record.get("headline", ""))
    creative_text = build_creative_text(body, headline)

    return {
        "ad_id": record.get("ad_archive_id", ""),
        "advertiser": clean_text(record.get("advertiser", "")),
        "ad_body": body,
        "headline": headline,
        "creative_text": creative_text,
        "cta": clean_text(record.get("cta", "")),
        "impression_raw": impression_raw,
        "impression_lower": imp_lower,
        "impression_upper": imp_upper,
        "impression_mid": imp_mid,
        "start_date": start_date.isoformat() if start_date else None,
        "longevity_days": longevity_days,
        "longevity_score": math.log1p(longevity_days),
        "platforms": record.get("platforms", []),
        "thumbnail_url": record.get("thumbnail_url", ""),
    }


def clean_all(
    input_path: Path = EXTRACTED_INPUT,
    output_path: Path = CLEAN_OUTPUT,
) -> list[dict[str, Any]]:
    """Normalize all extracted records. Returns the clean list."""
    records: list[dict[str, Any]] = []

    with input_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
                clean = normalize(raw)
                records.append(clean)
            except Exception as exc:
                print(f"[WARN] Skipping record: {exc}")

    with output_path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"[INFO] Cleaned {len(records)} ads → {output_path}")
    return records


if __name__ == "__main__":
    clean_all()
