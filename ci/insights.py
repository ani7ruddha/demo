"""
Insights generation module.

Classifies clusters by creative angle, detects saturation/opportunity,
extracts top hooks, and writes insights.md + insights.json.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SCORED_ADS_INPUT = DATA_DIR / "ads_scored.jsonl"
SCORED_CLUSTERS_INPUT = DATA_DIR / "clusters_scored.json"
INSIGHTS_MD_OUTPUT = DATA_DIR / "insights.md"
INSIGHTS_JSON_OUTPUT = DATA_DIR / "insights.json"

# ---------------------------------------------------------------------------
# Angle keyword maps
# ---------------------------------------------------------------------------

ANGLE_KEYWORDS: dict[str, list[str]] = {
    "Authority": [
        "doctor", "clinically", "clinically proven", "research", "scientist",
        "expert", "study", "medical", "fda", "dermatologist", "lab", "formula",
        "evidence", "peer-reviewed", "certified",
    ],
    "Fear": [
        "risk", "dangerous", "aging", "damage", "warning", "beware", "toxic",
        "harmful", "don't ignore", "problem", "disease", "symptom", "chronic",
        "losing", "wrinkle", "decline", "threat",
    ],
    "Aspiration": [
        "best shape", "confidence", "transformation", "dream", "achieve",
        "potential", "success", "glow", "radiant", "stronger", "thriving",
        "unstoppable", "level up", "upgrade", "peak", "powerful",
    ],
    "Savings": [
        "save", "discount", "free", "bundle", "deal", "offer", "off",
        "limited time", "promo", "clearance", "affordable", "cheap",
        "value", "% off", "sale", "coupon", "redeem",
    ],
    "Convenience": [
        "easy", "simple", "at home", "just minutes", "effortless", "quick",
        "no hassle", "done for you", "ready", "instantly", "on the go",
        "delivered", "auto", "one click", "without leaving",
    ],
    "Mechanism": [
        "how it works", "secret", "breakthrough", "proprietary", "patented",
        "unique formula", "technology", "method", "system", "process",
        "activate", "triggers", "blocks", "boosts", "mechanism",
    ],
    "Social Proof": [
        "thousands", "reviews", "rated", "customers", "people", "community",
        "bestseller", "popular", "loved", "verified", "testimonial",
        "stars", "recommended", "#1", "most popular",
    ],
    "Curiosity": [
        "secret", "hidden", "revealed", "what they don't tell", "shocking",
        "surprising", "little known", "trick", "hack", "weird", "unusual",
        "discover", "uncover", "truth", "finally",
    ],
    "Urgency": [
        "limited", "hurry", "expires", "today only", "last chance",
        "selling out", "while supplies", "act now", "don't wait",
        "deadline", "closing", "running out",
    ],
}


def classify_angle(text: str) -> tuple[str, dict[str, int]]:
    """
    Return (dominant_angle, {angle: hit_count}) for a text.
    """
    text_lower = text.lower()
    hit_counts: dict[str, int] = {}

    for angle, keywords in ANGLE_KEYWORDS.items():
        count = sum(1 for kw in keywords if kw in text_lower)
        if count:
            hit_counts[angle] = count

    if not hit_counts:
        return "Other", {}

    dominant = max(hit_counts, key=lambda k: hit_counts[k])
    return dominant, hit_counts


def assign_angles_to_clusters(
    clusters: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Classify each cluster's dominant angle based on its representative ad text."""
    for cid, cluster in clusters.items():
        rep_ad = cluster.get("representative_ad", {})
        text = (
            rep_ad.get("creative_text")
            or rep_ad.get("ad_body")
            or " ".join(cluster.get("top_keywords", []))
        )
        angle, _ = classify_angle(text)
        cluster["angle_type"] = angle
    return clusters


# ---------------------------------------------------------------------------
# Top hooks extraction
# ---------------------------------------------------------------------------

def extract_hooks(ads: list[dict[str, Any]], top_n: int = 20) -> list[str]:
    """
    Extract the top-N opening phrases (first 10 words) sorted by winner_score.
    """
    scored = sorted(ads, key=lambda a: a.get("winner_score", 0.0), reverse=True)
    hooks: list[str] = []
    seen: set[str] = set()

    for ad in scored[:100]:  # Look at top 100 ads
        text = ad.get("creative_text") or ad.get("ad_body") or ""
        if not text:
            continue
        # Take first sentence or first 10 words
        first_sentence = re.split(r"[.!?\n]", text)[0].strip()
        words = first_sentence.split()
        hook = " ".join(words[:10])
        if hook and hook not in seen and len(hook) > 15:
            seen.add(hook)
            hooks.append(hook)
        if len(hooks) >= top_n:
            break

    return hooks


# ---------------------------------------------------------------------------
# Underserved opportunity detection
# ---------------------------------------------------------------------------

def find_underserved(
    clusters: dict[str, dict[str, Any]],
    percentile_size: float = 40.0,
    percentile_score: float = 60.0,
) -> list[dict[str, Any]]:
    """
    Small clusters (below size percentile) with high winner score (above score percentile).
    These represent under-exploited but effective creative angles.
    """
    import numpy as np

    sizes = [c["size"] for c in clusters.values()]
    scores = [c.get("avg_winner_score", 0.0) for c in clusters.values()]

    if not sizes:
        return []

    size_thresh = float(np.percentile(sizes, percentile_size))
    score_thresh = float(np.percentile(scores, percentile_score))

    return [
        c for c in clusters.values()
        if c["size"] <= size_thresh and c.get("avg_winner_score", 0.0) >= score_thresh
    ]


# ---------------------------------------------------------------------------
# Main insight generation
# ---------------------------------------------------------------------------

def generate_insights(
    ads: list[dict[str, Any]] | None = None,
    clusters: dict[str, dict[str, Any]] | None = None,
    saturation: float = 0.0,
) -> dict[str, Any]:
    """
    Build insights dict. If ads/clusters not provided, loads from disk.
    """
    if ads is None:
        ads = []
        with SCORED_ADS_INPUT.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    ads.append(json.loads(line))

    if clusters is None:
        with SCORED_CLUSTERS_INPUT.open("r", encoding="utf-8") as f:
            clusters = json.load(f)

    # Assign angles
    clusters = assign_angles_to_clusters(clusters)

    cluster_list = list(clusters.values())

    # 1. Top 5 dominant angles
    angle_counts: Counter = Counter(c.get("angle_type", "Other") for c in cluster_list)
    top_angles = angle_counts.most_common(5)

    # 2. Highest impression cluster
    highest_imp_cluster = max(
        cluster_list, key=lambda c: c.get("avg_impression_mid", 0.0), default={}
    )

    # 3. Longest running cluster (by avg_longevity_days)
    longest_cluster = max(
        cluster_list, key=lambda c: c.get("avg_longevity_days", 0.0), default={}
    )

    # 4. Offer pattern distribution (angle distribution)
    angle_distribution = dict(angle_counts)

    # 5. Saturation (passed in or recomputed from clusters if 0)
    if saturation == 0.0:
        from ci.score import compute_saturation
        saturation = compute_saturation(clusters)

    # 6. Underserved opportunities
    underserved = find_underserved(clusters)

    # 7. Top hooks
    top_hooks = extract_hooks(ads, top_n=20)

    # Scalable clusters
    from ci.score import predict_scalable_clusters
    scalable = predict_scalable_clusters(clusters)

    insights = {
        "total_ads": len(ads),
        "total_clusters": len(cluster_list),
        "saturation_score": saturation,
        "top_angles": [{"angle": a, "cluster_count": c} for a, c in top_angles],
        "highest_impression_cluster": {
            "cluster_id": highest_imp_cluster.get("cluster_id"),
            "avg_impression_mid": highest_imp_cluster.get("avg_impression_mid"),
            "angle_type": highest_imp_cluster.get("angle_type"),
            "top_keywords": highest_imp_cluster.get("top_keywords"),
        },
        "longest_running_cluster": {
            "cluster_id": longest_cluster.get("cluster_id"),
            "avg_longevity_days": longest_cluster.get("avg_longevity_days"),
            "angle_type": longest_cluster.get("angle_type"),
            "top_keywords": longest_cluster.get("top_keywords"),
        },
        "angle_distribution": angle_distribution,
        "underserved_opportunities": [
            {
                "cluster_id": c.get("cluster_id"),
                "size": c.get("size"),
                "avg_winner_score": c.get("avg_winner_score"),
                "angle_type": c.get("angle_type"),
                "top_keywords": c.get("top_keywords"),
            }
            for c in underserved
        ],
        "top_hooks": top_hooks,
        "scalable_clusters": [
            {
                "cluster_id": c.get("cluster_id"),
                "size": c.get("size"),
                "avg_impression_mid": c.get("avg_impression_mid"),
                "avg_winner_score": c.get("avg_winner_score"),
                "angle_type": c.get("angle_type"),
                "top_keywords": c.get("top_keywords"),
            }
            for c in scalable
        ],
        # Full cluster list for dashboard
        "clusters": [
            {
                "cluster_id": c.get("cluster_id"),
                "size": c.get("size"),
                "avg_impression_mid": c.get("avg_impression_mid"),
                "avg_winner_score": c.get("avg_winner_score"),
                "angle_type": c.get("angle_type", "Other"),
                "top_keywords": c.get("top_keywords", []),
                "representative_ad": c.get("representative_ad", {}),
                "avg_longevity_days": c.get("avg_longevity_days", 0.0),
            }
            for c in sorted(
                cluster_list,
                key=lambda c: c.get("avg_winner_score", 0.0),
                reverse=True,
            )
        ],
    }

    # Write insights.json
    with INSIGHTS_JSON_OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(insights, f, indent=2, ensure_ascii=False)

    # Write insights.md
    _write_markdown(insights)

    # Update clusters with angle type (save back)
    with SCORED_CLUSTERS_INPUT.open("w", encoding="utf-8") as f:
        json.dump(clusters, f, indent=2, ensure_ascii=False)

    print(f"[INFO] Insights saved → {INSIGHTS_JSON_OUTPUT}")
    print(f"[INFO] Insights markdown → {INSIGHTS_MD_OUTPUT}")
    return insights


def _write_markdown(insights: dict[str, Any]) -> None:
    lines = [
        "# Creative Intelligence Dashboard — Insights Report",
        "",
        f"**Total Ads Analysed:** {insights['total_ads']}  ",
        f"**Total Clusters:** {insights['total_clusters']}  ",
        f"**Saturation Score (HHI):** {insights['saturation_score']:.4f}  ",
        "",
        "---",
        "",
        "## 1. Top 5 Dominant Angles",
        "",
    ]
    for i, entry in enumerate(insights["top_angles"], 1):
        lines.append(f"{i}. **{entry['angle']}** — {entry['cluster_count']} cluster(s)")
    lines += [
        "",
        "---",
        "",
        "## 2. Highest Impression Cluster",
        "",
    ]
    hi = insights["highest_impression_cluster"]
    lines += [
        f"- Cluster ID: `{hi['cluster_id']}`",
        f"- Avg Impressions (mid): `{hi['avg_impression_mid']:,.0f}`",
        f"- Angle: **{hi['angle_type']}**",
        f"- Top Keywords: {', '.join(hi['top_keywords'] or [])}",
        "",
        "---",
        "",
        "## 3. Longest Running Cluster",
        "",
    ]
    lr = insights["longest_running_cluster"]
    lines += [
        f"- Cluster ID: `{lr['cluster_id']}`",
        f"- Avg Days Running: `{lr['avg_longevity_days']:.0f}`",
        f"- Angle: **{lr['angle_type']}**",
        f"- Top Keywords: {', '.join(lr['top_keywords'] or [])}",
        "",
        "---",
        "",
        "## 4. Offer Pattern Distribution",
        "",
    ]
    for angle, count in sorted(
        insights["angle_distribution"].items(), key=lambda x: -x[1]
    ):
        lines.append(f"- **{angle}**: {count} cluster(s)")

    lines += [
        "",
        "---",
        "",
        "## 5. Saturation Score",
        "",
        f"HHI = `{insights['saturation_score']:.4f}`  ",
        "(0 = perfectly distributed, 1 = monopoly angle)",
        "",
        "---",
        "",
        "## 6. Underserved Opportunities",
        "",
    ]
    for opp in insights["underserved_opportunities"]:
        lines += [
            f"- Cluster `{opp['cluster_id']}` — Size: {opp['size']}, "
            f"Angle: **{opp['angle_type']}**, "
            f"Winner Score: {opp['avg_winner_score']:.2f}",
            f"  Keywords: {', '.join(opp['top_keywords'] or [])}",
        ]
    if not insights["underserved_opportunities"]:
        lines.append("_No clear underserved opportunities detected._")

    lines += [
        "",
        "---",
        "",
        "## 7. Top 20 High-Performing Hooks",
        "",
    ]
    for i, hook in enumerate(insights["top_hooks"], 1):
        lines.append(f"{i}. _{hook}_")

    lines += [
        "",
        "---",
        "",
        "## 8. Likely Winning Creative Themes (Scalable Clusters)",
        "",
    ]
    for c in insights["scalable_clusters"]:
        lines += [
            f"- **Cluster {c['cluster_id']}** | Angle: {c['angle_type']} | "
            f"Size: {c['size']} | Avg Imp: {c['avg_impression_mid']:,.0f} | "
            f"Score: {c['avg_winner_score']:.2f}",
            f"  Keywords: {', '.join(c['top_keywords'] or [])}",
        ]
    if not insights["scalable_clusters"]:
        lines.append("_No clusters met all three scalability criteria._")

    INSIGHTS_MD_OUTPUT.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    generate_insights()
