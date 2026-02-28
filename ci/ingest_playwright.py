"""
Playwright-based ingestion module for Meta Ads Library.

Launches Chromium, navigates to the Ads Library URL, scrolls until
max_ads are collected (or stalls), optionally sorts by impressions,
and saves raw ad card data to data/ads_raw.jsonl.
"""

from __future__ import annotations

import json
import random
import time
from pathlib import Path
from typing import Any

from playwright.sync_api import Page, sync_playwright

# ---------------------------------------------------------------------------
# CSS / XPath selector map — update here if Meta changes the DOM
# ---------------------------------------------------------------------------
SELECTORS: dict[str, str] = {
    # Container for a single ad card
    "ad_card": "div[class*='_8nqq']",
    # Fallback card selectors (tried in order if primary fails)
    "ad_card_fallbacks": [
        "div[class*='x8t9es0']",
        "div[class*='_7jyr']",
        "div[data-testid='ad-card']",
        "div[class*='xh8yej3']",
    ],
    # Sort / filter dropdown trigger
    "sort_button": "div[aria-label='Sort'], div[aria-label='Filter'], button[aria-label*='Sort']",
    # 'Highest impressions' menu option text
    "sort_option_text": "Highest impressions",
    # Library result count text
    "result_count": "div[class*='_8njc'] span",
    # Impression range label inside a card
    "impression_label": "span[class*='_8nqr'], div[class*='_8nqr']",
    # Advertiser / page name
    "advertiser": "a[class*='_231w'], span[class*='_231w'], strong",
    # Ad body text
    "ad_text": "div[class*='_4ik4'] div[class*='_4ik5']",
    # Headline / title
    "headline": "div[class*='_8jh2'], div[class*='_4ik4'] h4",
    # CTA button text
    "cta": "div[class*='_a2e0'], a[class*='_8jh5']",
    # Start date label
    "start_date": "span[class*='_8nlc']",
    # Platform icons alt text
    "platform_icons": "img[class*='_6mwt']",
    # Thumbnail / media image
    "thumbnail": "img[class*='_7jys'], div[class*='_7jyr'] img",
    # 'See more' expand button inside card
    "see_more": "span[role='button']:has-text('See More'), div[role='button']:has-text('See More')",
}

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RAW_OUTPUT = DATA_DIR / "ads_raw.jsonl"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _random_delay(low: float = 1.5, high: float = 3.0) -> None:
    time.sleep(random.uniform(low, high))


def _detect_card_selector(page: Page) -> str:
    """Try selectors in order; return the first that matches at least one element."""
    primary = SELECTORS["ad_card"]
    if page.locator(primary).count() > 0:
        return primary
    for fallback in SELECTORS["ad_card_fallbacks"]:
        if page.locator(fallback).count() > 0:
            return fallback
    # Last resort — print first 2 000 chars of body for debugging
    body_html = page.inner_html("body")[:2000]
    print("[WARN] No ad card selector matched. Body snippet:\n", body_html)
    return primary  # return primary anyway so downstream can handle 0 cards


def _try_sort_by_impressions(page: Page) -> bool:
    """
    Try to click the sort dropdown and select 'Highest impressions'.
    Returns True if successful, False otherwise.
    """
    try:
        sort_btn = page.locator(SELECTORS["sort_button"]).first
        if sort_btn.count() == 0:
            print("[INFO] Sort dropdown not found — skipping sort step.")
            return False
        sort_btn.click()
        page.wait_for_timeout(1500)
        # Look for the menu option by text
        option = page.get_by_text(SELECTORS["sort_option_text"], exact=False).first
        if option.count() == 0:
            print("[INFO] 'Highest impressions' option not found in dropdown.")
            # Close dropdown by pressing Escape
            page.keyboard.press("Escape")
            return False
        option.click()
        page.wait_for_timeout(2000)
        print("[INFO] Sorted by Highest Impressions.")
        return True
    except Exception as exc:
        print(f"[WARN] Could not apply sort: {exc}")
        return False


def _extract_card_html(page: Page, card_selector: str) -> list[dict[str, Any]]:
    """Return list of raw dicts with outerHTML + basic attributes per card."""
    cards = page.locator(card_selector).all()
    results = []
    for card in cards:
        try:
            outer = card.inner_html()
            # Pull aria-label or data-id if present
            aria = card.get_attribute("aria-label") or ""
            data_id = card.get_attribute("data-id") or ""
            results.append({"html": outer, "aria_label": aria, "data_id": data_id})
        except Exception:
            pass
    return results


# ---------------------------------------------------------------------------
# Main ingestion function
# ---------------------------------------------------------------------------

def ingest(
    ads_library_url: str,
    max_ads: int = 300,
    headless: bool = True,
    output_path: Path = RAW_OUTPUT,
) -> list[dict[str, Any]]:
    """
    Open the Meta Ads Library URL with Playwright, scroll to collect up to
    `max_ads` ad cards, and persist raw HTML + metadata to JSONL.

    Returns the list of raw ad dicts.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    all_ads: list[dict[str, Any]] = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=headless,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ],
        )
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()

        print(f"[INFO] Navigating to: {ads_library_url}")
        page.goto(ads_library_url, wait_until="domcontentloaded", timeout=60_000)
        _random_delay(3, 5)

        # Detect which CSS selector finds ad cards on this page
        card_selector = _detect_card_selector(page)
        print(f"[INFO] Using card selector: {card_selector}")

        # Optionally sort by highest impressions
        _try_sort_by_impressions(page)
        _random_delay(2, 3)

        # ------------------------------------------------------------------ #
        # Scroll loop
        # ------------------------------------------------------------------ #
        stall_count = 0
        max_stalls = 3

        while len(all_ads) < max_ads and stall_count < max_stalls:
            # Collect current cards
            current_batch = _extract_card_html(page, card_selector)
            prev_count = len(all_ads)

            # Merge by dedup on html snippet (first 200 chars as key)
            existing_keys = {a["html"][:200] for a in all_ads}
            new_cards = [c for c in current_batch if c["html"][:200] not in existing_keys]
            all_ads.extend(new_cards)

            print(f"[INFO] Cards collected so far: {len(all_ads)} / {max_ads}")

            if len(all_ads) >= max_ads:
                break

            if len(all_ads) == prev_count:
                stall_count += 1
                print(f"[INFO] No new ads loaded (stall {stall_count}/{max_stalls})")
            else:
                stall_count = 0  # reset on progress

            # Scroll down
            page.evaluate("window.scrollBy(0, window.innerHeight * 2)")
            _random_delay(1.5, 3.0)

            # Try clicking a "Load more" / "See more" button if present
            try:
                load_more = page.get_by_role("button", name="See more results").first
                if load_more.is_visible():
                    load_more.click()
                    _random_delay(2, 3)
            except Exception:
                pass

        browser.close()

    # Trim to max_ads
    all_ads = all_ads[:max_ads]
    print(f"[INFO] Total ads captured: {len(all_ads)}")

    # Persist to JSONL
    with output_path.open("w", encoding="utf-8") as f:
        for ad in all_ads:
            f.write(json.dumps(ad, ensure_ascii=False) + "\n")

    print(f"[INFO] Raw data saved → {output_path}")
    return all_ads


if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=US&q=fitness&search_type=keyword_unordered&media_type=all"
    ingest(url, max_ads=50, headless=True)
