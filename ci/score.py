"""
Winner score computation module.

Winner Score = log(impression_mid + 1)
             + longevity_score
             + cluster_density_weight

Where:
  longevity_score      = log(days_running + 1)  [already in clean data]
  cluster_density_weight = log(cluster_avg_imp + 1) / log(global_max_imp + 1) * 2

Also implements predict_scalable_clusters() for bonus performance prediction.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CLUSTERED_INPUT = DATA_DIR / "ads_clustered.jsonl"
CLUSTERS_INPUT = DATA_DIR / "clusters.json"
SCORED_ADS_OUTPUT = DATA_DIR / "ads_scored.jsonl"
SCORED_CLUSTERS_OUTPUT = DATA_DIR / "clusters_scored.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_ads(path: Path) -> list[dict[str, Any]]:
    ads = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                ads.append(json.loads(line))
    return ads


def _load_clusters(path: Path) -> dict[str, dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def compute_cluster_density_weights(
    clusters: dict[str, dict[str, Any]],
) -> dict[str, float]:
    """
    For each cluster, compute a density weight based on avg impression_mid
    relative to the global max.
    """
    all_avgs = [c["avg_impression_mid"] for c in clusters.values()]
    global_max = max(all_avgs) if all_avgs else 1.0

    weights = {}
    for cid, cluster in clusters.items():
        avg = cluster["avg_impression_mid"]
        weight = math.log1p(avg) / math.log1p(global_max + 1) * 2.0
        weights[cid] = weight
    return weights


def score_ads(
    ads: list[dict[str, Any]],
    cluster_density_weights: dict[str, float],
) -> list[dict[str, Any]]:
    """Attach winner_score to each ad dict."""
    for ad in ads:
        imp_mid = ad.get("impression_mid", 0.0) or 0.0
        longevity = ad.get("longevity_score", 0.0) or 0.0
        cid = str(ad.get("cluster_id", -1))
        density_w = cluster_density_weights.get(cid, 0.0)

        winner_score = math.log1p(imp_mid) + longevity + density_w
        ad["winner_score"] = round(winner_score, 4)

    return ads


def update_cluster_scores(
    clusters: dict[str, dict[str, Any]],
    ads: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Attach avg_winner_score and max_winner_score to each cluster."""
    cluster_scores: dict[str, list[float]] = {cid: [] for cid in clusters}
    cluster_longevity: dict[str, list[float]] = {cid: [] for cid in clusters}

    for ad in ads:
        cid = str(ad.get("cluster_id", -1))
        if cid in cluster_scores:
            cluster_scores[cid].append(ad.get("winner_score", 0.0))
            cluster_longevity[cid].append(ad.get("longevity_days", 0.0))

    for cid, cluster in clusters.items():
        scores = cluster_scores.get(cid, [])
        cluster["avg_winner_score"] = float(np.mean(scores)) if scores else 0.0
        cluster["max_winner_score"] = float(np.max(scores)) if scores else 0.0
        longs = cluster_longevity.get(cid, [])
        cluster["avg_longevity_days"] = float(np.mean(longs)) if longs else 0.0

    return clusters


# ---------------------------------------------------------------------------
# Herfindahl Saturation Index
# ---------------------------------------------------------------------------

def compute_saturation(clusters: dict[str, dict[str, Any]]) -> float:
    """
    Cluster Concentration Index (Herfindahl Index).
    = sum( (cluster_size / total_ads)^2 )
    High value (→1) = market concentrated in few angles.
    Low value (→0)  = many equally sized clusters.
    """
    total = sum(c["size"] for c in clusters.values())
    if total == 0:
        return 0.0
    hhi = sum((c["size"] / total) ** 2 for c in clusters.values())
    return round(hhi, 4)


# ---------------------------------------------------------------------------
# Scalable cluster prediction (bonus)
# ---------------------------------------------------------------------------

def predict_scalable_clusters(
    clusters: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Return clusters ranked by likelihood of being 'winning' themes.

    Criteria:
    - avg_impression_mid > median across all clusters
    - avg_longevity_days > median across all clusters
    - size > 3
    """
    cluster_list = list(clusters.values())

    imp_values = [c["avg_impression_mid"] for c in cluster_list]
    lon_values = [c["avg_longevity_days"] for c in cluster_list]

    if not imp_values:
        return []

    median_imp = float(np.median(imp_values))
    median_lon = float(np.median(lon_values))

    scalable = [
        c for c in cluster_list
        if c["avg_impression_mid"] > median_imp
        and c["avg_longevity_days"] > median_lon
        and c["size"] > 3
    ]

    # Sort by avg_winner_score descending
    scalable.sort(key=lambda c: c.get("avg_winner_score", 0.0), reverse=True)
    return scalable


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_scoring(
    ads: list[dict[str, Any]] | None = None,
    clusters: dict[str, dict[str, Any]] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], float]:
    """
    Compute winner scores for all ads and cluster aggregates.

    Returns (scored_ads, scored_clusters, saturation_index).
    """
    if ads is None:
        ads = _load_ads(CLUSTERED_INPUT)
    if clusters is None:
        clusters = _load_clusters(CLUSTERS_INPUT)

    density_weights = compute_cluster_density_weights(clusters)
    ads = score_ads(ads, density_weights)
    clusters = update_cluster_scores(clusters, ads)
    saturation = compute_saturation(clusters)

    print(f"[INFO] Saturation index (HHI): {saturation:.4f}")

    # Save
    with SCORED_ADS_OUTPUT.open("w", encoding="utf-8") as f:
        for ad in ads:
            f.write(json.dumps(ad, ensure_ascii=False) + "\n")

    with SCORED_CLUSTERS_OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(clusters, f, indent=2, ensure_ascii=False)

    print(f"[INFO] Scored ads → {SCORED_ADS_OUTPUT}")
    print(f"[INFO] Scored clusters → {SCORED_CLUSTERS_OUTPUT}")
    return ads, clusters, saturation


if __name__ == "__main__":
    run_scoring()
