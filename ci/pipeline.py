"""
CI Pipeline — orchestrates the full ingestion → insights flow.

Usage:
  python -m ci.pipeline --url "<ads_library_url>" --max_ads 300 --headless false

Or import and call run_pipeline() from the Streamlit app.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def run_pipeline(
    url: str,
    max_ads: int = 300,
    headless: bool = True,
    skip_ingest: bool = False,
    use_umap: bool = True,
    min_cluster_size: int = 3,
) -> dict[str, Any]:
    """
    Run the full pipeline end-to-end.

    Parameters
    ----------
    url             : Meta Ads Library URL to scrape.
    max_ads         : Maximum number of ad cards to collect.
    headless        : Whether to run Chromium in headless mode.
    skip_ingest     : If True, skip scraping and use existing data/ads_raw.jsonl.
    use_umap        : Whether to apply UMAP dimensionality reduction.
    min_cluster_size: Minimum cluster size for HDBSCAN.

    Returns
    -------
    insights dict (also saved to data/insights.json).
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    # ------------------------------------------------------------------ #
    # Step 1: Ingest
    # ------------------------------------------------------------------ #
    if not skip_ingest:
        print("\n=== STEP 1: Playwright Ingestion ===")
        from ci.ingest_playwright import ingest
        ingest(url, max_ads=max_ads, headless=headless)
    else:
        print("\n[INFO] Skipping ingestion — using cached ads_raw.jsonl")

    # ------------------------------------------------------------------ #
    # Step 2: Extract
    # ------------------------------------------------------------------ #
    print("\n=== STEP 2: Extraction ===")
    from ci.extract import extract_all
    extracted = extract_all()

    if not extracted:
        raise RuntimeError(
            "Extraction returned 0 ads. Check the URL and selector map in "
            "ci/ingest_playwright.py → SELECTORS."
        )

    # ------------------------------------------------------------------ #
    # Step 3: Clean / Normalize
    # ------------------------------------------------------------------ #
    print("\n=== STEP 3: Normalisation ===")
    from ci.clean import clean_all
    clean_ads = clean_all()

    # ------------------------------------------------------------------ #
    # Step 4: Embed
    # ------------------------------------------------------------------ #
    print("\n=== STEP 4: Embeddings ===")
    from ci.embed import run_embeddings
    cluster_embeddings, umap_2d, ads_from_embed = run_embeddings(use_umap=use_umap)

    # ------------------------------------------------------------------ #
    # Step 5: Cluster
    # ------------------------------------------------------------------ #
    print("\n=== STEP 5: Clustering ===")
    from ci.cluster import run_clustering
    clusters, labels = run_clustering(
        ads=clean_ads,
        embeddings=cluster_embeddings,
        min_cluster_size=min_cluster_size,
    )

    # ------------------------------------------------------------------ #
    # Step 6: Score
    # ------------------------------------------------------------------ #
    print("\n=== STEP 6: Winner Scoring ===")
    from ci.score import run_scoring
    # Reload clustered ads (cluster_id attached)
    scored_ads_path = DATA_DIR / "ads_clustered.jsonl"
    clustered_ads = []
    with scored_ads_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                clustered_ads.append(json.loads(line))

    scored_ads, scored_clusters, saturation = run_scoring(
        ads=clustered_ads,
        clusters={str(k): v for k, v in clusters.items()},
    )

    # ------------------------------------------------------------------ #
    # Step 7: Insights
    # ------------------------------------------------------------------ #
    print("\n=== STEP 7: Insight Generation ===")
    from ci.insights import generate_insights
    insights = generate_insights(
        ads=scored_ads,
        clusters=scored_clusters,
        saturation=saturation,
    )

    elapsed = time.time() - t0
    print(f"\n✓ Pipeline complete in {elapsed:.1f}s")
    print(f"  Total ads: {insights['total_ads']}")
    print(f"  Clusters : {insights['total_clusters']}")
    print(f"  HHI      : {insights['saturation_score']:.4f}")
    print(f"  Insights → {DATA_DIR / 'insights.json'}")
    print(f"  Report   → {DATA_DIR / 'insights.md'}")

    return insights


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Creative Intelligence Pipeline — Meta Ads Library",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--url", required=True, help="Meta Ads Library URL to scrape")
    p.add_argument("--max_ads", type=int, default=300, help="Max ads to collect")
    p.add_argument(
        "--headless",
        type=lambda x: x.lower() not in ("false", "0", "no"),
        default=True,
        help="Run browser headless (true/false)",
    )
    p.add_argument(
        "--skip_ingest",
        action="store_true",
        help="Skip ingestion and reuse existing ads_raw.jsonl",
    )
    p.add_argument(
        "--no_umap",
        action="store_true",
        help="Disable UMAP reduction (use raw embeddings for clustering)",
    )
    p.add_argument(
        "--min_cluster_size",
        type=int,
        default=3,
        help="Minimum cluster size for HDBSCAN",
    )
    return p


if __name__ == "__main__":
    args = _build_parser().parse_args()
    run_pipeline(
        url=args.url,
        max_ads=args.max_ads,
        headless=args.headless,
        skip_ingest=args.skip_ingest,
        use_umap=not args.no_umap,
        min_cluster_size=args.min_cluster_size,
    )
