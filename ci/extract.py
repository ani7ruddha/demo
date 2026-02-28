"""
Extraction module: parses raw HTML from ad cards into structured dicts.

Uses BeautifulSoup to parse the per-card HTML stored in ads_raw.jsonl
and outputs structured records to data/ads_extracted.jsonl.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RAW_INPUT = DATA_DIR / "ads_raw.jsonl"
EXTRACTED_OUTPUT = DATA_DIR / "ads_extracted.jsonl"

# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------

_IMPRESSION_PATTERN = re.compile(
    r"([\d,.]+[KkMmBb]?)\s*[–\-–—]\s*([\d,.]+[KkMmBb]?)\s*impressions?",
    re.IGNORECASE,
)
_IMPRESSION_LOWER_PATTERN = re.compile(
    r"([\d,.]+[KkMmBb]?)\+?\s*impressions?",
    re.IGNORECASE,
)
_DATE_PATTERN = re.compile(
    r"(Started running on|Active since|Started|Running since)\s+(.+?)(?:\.|$)",
    re.IGNORECASE,
)
_ARCHIVE_ID_PATTERN = re.compile(r"id=(\d+)", re.IGNORECASE)


def _text(tag: Any) -> str:
    return tag.get_text(separator=" ", strip=True) if tag else ""


def _first_text(soup: BeautifulSoup, *selectors: str) -> str:
    for sel in selectors:
        tag = soup.select_one(sel)
        if tag:
            return _text(tag)
    return ""


def _all_text(soup: BeautifulSoup, selector: str) -> list[str]:
    return [_text(t) for t in soup.select(selector) if _text(t)]


def _extract_archive_id(soup: BeautifulSoup, aria_label: str, data_id: str) -> str:
    # Try data-id attribute first
    if data_id:
        return data_id
    # Try links inside card
    for a in soup.find_all("a", href=True):
        m = _ARCHIVE_ID_PATTERN.search(a["href"])
        if m:
            return m.group(1)
    # Try aria-label
    m = re.search(r"(\d{10,})", aria_label)
    if m:
        return m.group(1)
    return ""


def _extract_advertiser(soup: BeautifulSoup) -> str:
    # Common patterns: strong tag, anchor with page link
    for sel in [
        "a[href*='facebook.com/']",
        "strong",
        "span[class*='_231w']",
        "a[class*='_8njj']",
        "h4",
    ]:
        tag = soup.select_one(sel)
        if tag:
            text = _text(tag)
            if text and len(text) < 100:
                return text
    return ""


def _extract_ad_body(soup: BeautifulSoup) -> str:
    # Ad body is often in a large div after the advertiser header
    candidates = []
    for sel in [
        "div[class*='_4ik4'] div[class*='_4ik5']",
        "div[class*='_7jyr'] div[class*='_4ik4']",
        "div[data-testid='ad-creative-body']",
        "div[class*='x3nfvp2']",
        "p",
    ]:
        for tag in soup.select(sel):
            t = _text(tag)
            if t and len(t) > 20:
                candidates.append(t)
    # Return the longest candidate (likely the ad body)
    return max(candidates, key=len) if candidates else ""


def _extract_headline(soup: BeautifulSoup) -> str:
    for sel in [
        "div[class*='_8jh2']",
        "h4",
        "div[class*='x1iorvi4']",
        "div[class*='_4ik4'] h3",
        "div[class*='_4ik4'] h4",
    ]:
        tag = soup.select_one(sel)
        if tag:
            t = _text(tag)
            if t and len(t) < 200:
                return t
    return ""


def _extract_cta(soup: BeautifulSoup) -> str:
    for sel in [
        "div[class*='_a2e0']",
        "a[class*='_8jh5']",
        "a[role='button']",
        "div[role='button']",
        "button",
    ]:
        tag = soup.select_one(sel)
        if tag:
            t = _text(tag)
            if t and len(t) < 50:
                return t
    return ""


def _extract_impressions(soup: BeautifulSoup) -> str:
    full_text = soup.get_text(separator=" ")
    m = _IMPRESSION_PATTERN.search(full_text)
    if m:
        return m.group(0)
    m = _IMPRESSION_LOWER_PATTERN.search(full_text)
    if m:
        return m.group(0)
    return ""


def _extract_start_date(soup: BeautifulSoup) -> str:
    full_text = soup.get_text(separator=" ")
    m = _DATE_PATTERN.search(full_text)
    if m:
        return m.group(2).strip()
    return ""


def _extract_platforms(soup: BeautifulSoup) -> list[str]:
    platforms = []
    for img in soup.find_all("img"):
        alt = (img.get("alt") or "").lower()
        title = (img.get("title") or "").lower()
        for platform in ["facebook", "instagram", "messenger", "whatsapp", "audience network"]:
            if platform in alt or platform in title:
                platforms.append(platform.title())
    return list(set(platforms))


def _extract_thumbnail(soup: BeautifulSoup) -> str:
    for sel in [
        "img[class*='_7jys']",
        "div[class*='_7jyr'] img",
        "div[class*='x3nfvp2'] img",
        "img",
    ]:
        tag = soup.select_one(sel)
        if tag:
            src = tag.get("src") or tag.get("data-src") or ""
            if src and "http" in src:
                return src
    return ""


# ---------------------------------------------------------------------------
# Main extraction function
# ---------------------------------------------------------------------------

def extract_ad(raw: dict[str, Any]) -> dict[str, Any]:
    """Parse one raw card dict into a structured ad record."""
    soup = BeautifulSoup(raw.get("html", ""), "html.parser")
    aria_label = raw.get("aria_label", "")
    data_id = raw.get("data_id", "")

    return {
        "ad_archive_id": _extract_archive_id(soup, aria_label, data_id),
        "advertiser": _extract_advertiser(soup),
        "ad_body": _extract_ad_body(soup),
        "headline": _extract_headline(soup),
        "cta": _extract_cta(soup),
        "impression_raw": _extract_impressions(soup),
        "start_date_raw": _extract_start_date(soup),
        "platforms": _extract_platforms(soup),
        "thumbnail_url": _extract_thumbnail(soup),
        # Keep raw text for debugging
        "_full_text": soup.get_text(separator=" ", strip=True)[:500],
    }


def extract_all(
    input_path: Path = RAW_INPUT,
    output_path: Path = EXTRACTED_OUTPUT,
) -> list[dict[str, Any]]:
    """Extract all raw ads from JSONL and return structured list."""
    records: list[dict[str, Any]] = []

    with input_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
                record = extract_ad(raw)
                records.append(record)
            except Exception as exc:
                print(f"[WARN] Skipping record due to error: {exc}")

    with output_path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"[INFO] Extracted {len(records)} ads → {output_path}")
    return records


if __name__ == "__main__":
    extract_all()
