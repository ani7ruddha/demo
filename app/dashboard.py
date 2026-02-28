"""
Creative Intelligence Dashboard — Streamlit UI.

Run with:
  streamlit run app/dashboard.py
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import streamlit as st

# Ensure project root is on the path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DATA_DIR = ROOT / "data"

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Creative Intelligence Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    .kpi-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d6a9f 100%);
        border-radius: 12px;
        padding: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .kpi-value { font-size: 2.2rem; font-weight: 700; margin: 4px 0; }
    .kpi-label { font-size: 0.85rem; opacity: 0.8; text-transform: uppercase; letter-spacing: 1px; }
    .angle-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        background: #e8f4fd;
        color: #1a5276;
    }
    .winning-badge {
        background: linear-gradient(90deg, #f7971e, #ffd200);
        color: #1a1a1a;
        border-radius: 6px;
        padding: 2px 8px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar — controls
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("🎯 Creative Intelligence")
    st.markdown("---")

    ads_url = st.text_input(
        "Meta Ads Library URL",
        placeholder="https://www.facebook.com/ads/library/?...",
        help="Paste the full Ads Library search URL.",
    )

    col1, col2 = st.columns(2)
    with col1:
        max_ads = st.number_input("Max Ads", min_value=10, max_value=1000, value=300, step=10)
    with col2:
        min_cluster_size = st.number_input("Min Cluster Size", min_value=2, max_value=20, value=3)

    headless = st.toggle("Headless Browser", value=True)
    use_umap = st.toggle("Use UMAP", value=True)

    run_btn = st.button("🚀 Run Analysis", type="primary", use_container_width=True)

    st.markdown("---")

    # Load existing results if available
    load_existing = st.button("📂 Load Existing Results", use_container_width=True)

    st.markdown("---")
    st.caption("No API. Browser automation only.")
    st.caption("Meta Ads Library — public data.")

# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------

if "insights" not in st.session_state:
    st.session_state["insights"] = None
if "ads_df" not in st.session_state:
    st.session_state["ads_df"] = None
if "umap_2d" not in st.session_state:
    st.session_state["umap_2d"] = None


def _load_from_disk() -> bool:
    """Try to load previously computed results from data/."""
    insights_path = DATA_DIR / "insights.json"
    ads_path = DATA_DIR / "ads_scored.jsonl"
    umap_path = DATA_DIR / "umap_2d.npy"

    if not insights_path.exists():
        st.error("No insights.json found. Run the analysis first.")
        return False

    with insights_path.open("r") as f:
        st.session_state["insights"] = json.load(f)

    if ads_path.exists():
        ads = []
        with ads_path.open("r") as f:
            for line in f:
                line = line.strip()
                if line:
                    ads.append(json.loads(line))
        st.session_state["ads_df"] = pd.DataFrame(ads)

    if umap_path.exists():
        st.session_state["umap_2d"] = np.load(umap_path)

    return True


# ---------------------------------------------------------------------------
# Run pipeline on button click
# ---------------------------------------------------------------------------

if run_btn:
    if not ads_url.strip():
        st.error("Please enter a Meta Ads Library URL.")
    else:
        with st.spinner("Running pipeline… This may take a few minutes."):
            try:
                from ci.pipeline import run_pipeline  # noqa: PLC0415

                progress_bar = st.progress(0, text="Launching browser…")
                insights = run_pipeline(
                    url=ads_url.strip(),
                    max_ads=int(max_ads),
                    headless=headless,
                    use_umap=use_umap,
                    min_cluster_size=int(min_cluster_size),
                )
                progress_bar.progress(100, text="Done!")
                st.session_state["insights"] = insights
                _load_from_disk()  # refresh ads_df + umap_2d
                st.success(
                    f"Analysis complete — {insights['total_ads']} ads, "
                    f"{insights['total_clusters']} clusters."
                )
            except Exception as exc:
                st.error(f"Pipeline error: {exc}")
                st.exception(exc)

if load_existing:
    _load_from_disk()

# ---------------------------------------------------------------------------
# Main dashboard (shown when insights are loaded)
# ---------------------------------------------------------------------------

insights: dict[str, Any] | None = st.session_state.get("insights")
ads_df: pd.DataFrame | None = st.session_state.get("ads_df")
umap_2d: np.ndarray | None = st.session_state.get("umap_2d")

if insights is None:
    # Landing / empty state
    st.title("🎯 Creative Intelligence Dashboard")
    st.markdown(
        """
        Welcome! This dashboard analyses Meta Ads Library ad creatives using:

        - **Playwright** browser automation (no API)
        - **Sentence-transformers** embeddings
        - **HDBSCAN** clustering
        - **Winner scoring** based on impressions × longevity

        **To get started:**
        1. Paste a Meta Ads Library URL in the sidebar
        2. Configure options
        3. Click **Run Analysis**

        Or click **Load Existing Results** to view a previous run.
        """
    )
    st.stop()

# ------------------------------------------------------------------ #
# KPI Row
# ------------------------------------------------------------------ #

st.title("🎯 Creative Intelligence Dashboard")
st.markdown("---")

kpi_cols = st.columns(4)

avg_score = 0.0
if ads_df is not None and "winner_score" in ads_df.columns:
    avg_score = ads_df["winner_score"].mean()

with kpi_cols[0]:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-value">{insights["total_ads"]}</div>'
        f'<div class="kpi-label">Ads Scraped</div></div>',
        unsafe_allow_html=True,
    )
with kpi_cols[1]:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-value">{insights["total_clusters"]}</div>'
        f'<div class="kpi-label">Clusters Found</div></div>',
        unsafe_allow_html=True,
    )
with kpi_cols[2]:
    sat = insights["saturation_score"]
    sat_label = "Low" if sat < 0.2 else ("Medium" if sat < 0.4 else "High")
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-value">{sat:.3f}</div>'
        f'<div class="kpi-label">Saturation (HHI) — {sat_label}</div></div>',
        unsafe_allow_html=True,
    )
with kpi_cols[3]:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-value">{avg_score:.2f}</div>'
        f'<div class="kpi-label">Avg Winner Score</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ------------------------------------------------------------------ #
# Tabs
# ------------------------------------------------------------------ #

tab_overview, tab_clusters, tab_detail, tab_hooks, tab_viz = st.tabs(
    ["📊 Overview", "🗂 Clusters", "🔍 Cluster Detail", "🪝 Top Hooks", "📈 Visualisations"]
)

# ====================================================================
# TAB 1: Overview
# ====================================================================

with tab_overview:
    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.subheader("Top Dominant Angles")
        if insights.get("top_angles"):
            angle_df = pd.DataFrame(insights["top_angles"])
            st.bar_chart(angle_df.set_index("angle")["cluster_count"])

        st.subheader("Saturation Analysis")
        sat_val = insights["saturation_score"]
        st.metric("HHI Index", f"{sat_val:.4f}", help="0=diverse, 1=monopoly")
        if sat_val < 0.15:
            st.success("Market is highly fragmented — many angle opportunities.")
        elif sat_val < 0.35:
            st.warning("Moderate concentration. A few angles dominate.")
        else:
            st.error("High saturation — market dominated by 1-2 angles.")

    with col_b:
        st.subheader("Underserved Opportunities")
        opps = insights.get("underserved_opportunities", [])
        if opps:
            for opp in opps:
                with st.expander(
                    f"Cluster {opp['cluster_id']} — {opp['angle_type']} "
                    f"(Score: {opp['avg_winner_score']:.2f})"
                ):
                    st.write(f"**Size:** {opp['size']} ads")
                    st.write(f"**Keywords:** {', '.join(opp['top_keywords'] or [])}")
        else:
            st.info("No underserved opportunities detected in this data set.")

        st.subheader("Likely Winning Themes")
        scalable = insights.get("scalable_clusters", [])
        if scalable:
            for c in scalable[:5]:
                st.markdown(
                    f'<span class="winning-badge">★ WINNING</span> '
                    f"**Cluster {c['cluster_id']}** — {c['angle_type']} | "
                    f"Score: {c['avg_winner_score']:.2f} | "
                    f"{', '.join(c['top_keywords'] or [])}",
                    unsafe_allow_html=True,
                )
        else:
            st.info("Not enough data to predict scalable clusters.")

# ====================================================================
# TAB 2: Cluster Table
# ====================================================================

with tab_clusters:
    st.subheader("All Clusters — Ranked by Winner Score")

    cluster_data = insights.get("clusters", [])
    if cluster_data:
        cluster_df = pd.DataFrame(
            [
                {
                    "Cluster ID": c["cluster_id"],
                    "Size": c["size"],
                    "Angle": c["angle_type"],
                    "Avg Impressions": f"{c['avg_impression_mid']:,.0f}",
                    "Avg Longevity (days)": f"{c['avg_longevity_days']:.0f}",
                    "Winner Score": f"{c['avg_winner_score']:.3f}",
                    "Keywords": ", ".join(c["top_keywords"] or []),
                }
                for c in cluster_data
            ]
        )

        # Highlight scalable clusters
        scalable_ids = {
            c["cluster_id"] for c in insights.get("scalable_clusters", [])
        }

        def _style_row(row: pd.Series) -> list[str]:
            if row["Cluster ID"] in scalable_ids:
                return ["background-color: rgba(255, 210, 0, 0.15)"] * len(row)
            return [""] * len(row)

        st.dataframe(
            cluster_df.style.apply(_style_row, axis=1),
            use_container_width=True,
            hide_index=True,
        )
        st.caption("★ Gold-highlighted rows = predicted winning themes")
    else:
        st.info("No cluster data available.")

# ====================================================================
# TAB 3: Cluster Detail
# ====================================================================

with tab_detail:
    st.subheader("Cluster Detail View")

    cluster_data = insights.get("clusters", [])
    if not cluster_data:
        st.info("No cluster data available.")
    else:
        cluster_ids = [f"Cluster {c['cluster_id']} — {c['angle_type']}" for c in cluster_data]
        selected_label = st.selectbox("Select a cluster", cluster_ids)
        selected_idx = cluster_ids.index(selected_label)
        selected_cluster = cluster_data[selected_idx]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Size", selected_cluster["size"])
        col2.metric("Avg Impressions", f"{selected_cluster['avg_impression_mid']:,.0f}")
        col3.metric("Winner Score", f"{selected_cluster['avg_winner_score']:.3f}")
        col4.metric("Longevity (days)", f"{selected_cluster['avg_longevity_days']:.0f}")

        st.markdown(f"**Angle:** {selected_cluster['angle_type']}")
        st.markdown(f"**Top Keywords:** {', '.join(selected_cluster['top_keywords'] or [])}")

        st.divider()
        st.markdown("#### Representative Ad")
        rep = selected_cluster.get("representative_ad", {})
        if rep:
            if rep.get("thumbnail_url"):
                st.image(rep["thumbnail_url"], width=300)
            st.markdown(f"**Advertiser:** {rep.get('advertiser', 'N/A')}")
            st.markdown(f"**Headline:** {rep.get('headline', 'N/A')}")
            st.markdown(f"**Body:** {rep.get('ad_body', 'N/A')}")
            st.markdown(f"**CTA:** {rep.get('cta', 'N/A')}")
            st.markdown(f"**Impressions:** {rep.get('impression_raw', 'N/A')}")
            st.markdown(f"**Started:** {rep.get('start_date', 'N/A')}")
        else:
            st.info("No representative ad available.")

        # Show ads in this cluster
        st.divider()
        st.markdown("#### Ads in This Cluster")
        if ads_df is not None and "cluster_id" in ads_df.columns:
            cluster_ads = ads_df[
                ads_df["cluster_id"] == selected_cluster["cluster_id"]
            ].copy()
            if not cluster_ads.empty:
                display_cols = [
                    c for c in [
                        "advertiser", "creative_text", "impression_raw",
                        "winner_score", "start_date", "cta",
                    ]
                    if c in cluster_ads.columns
                ]
                st.dataframe(
                    cluster_ads[display_cols].sort_values(
                        "winner_score", ascending=False
                    ),
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("No individual ads loaded for this cluster.")
        else:
            st.info("Load ads_scored.jsonl to see individual ads per cluster.")

# ====================================================================
# TAB 4: Top Hooks
# ====================================================================

with tab_hooks:
    st.subheader("Top 20 High-Performing Hooks")
    st.markdown(
        "These are the opening phrases from the highest-scoring ads. "
        "Use them as inspiration for new ad copy."
    )

    hooks = insights.get("top_hooks", [])
    if hooks:
        for i, hook in enumerate(hooks, 1):
            st.markdown(f"**{i}.** _{hook}_")
    else:
        st.info("No hooks extracted yet.")

    st.divider()
    st.subheader("Angle Distribution")
    angle_dist = insights.get("angle_distribution", {})
    if angle_dist:
        angle_dist_df = pd.DataFrame(
            [{"Angle": k, "Clusters": v} for k, v in angle_dist.items()]
        ).sort_values("Clusters", ascending=False)
        st.bar_chart(angle_dist_df.set_index("Angle")["Clusters"])

# ====================================================================
# TAB 5: Visualisations
# ====================================================================

with tab_viz:
    st.subheader("Visualisations")

    col_v1, col_v2 = st.columns(2)

    with col_v1:
        st.markdown("#### Cluster Size Distribution")
        cluster_data = insights.get("clusters", [])
        if cluster_data:
            size_df = pd.DataFrame(
                [{"Cluster": f"C{c['cluster_id']}", "Size": c["size"]} for c in cluster_data]
            ).sort_values("Size", ascending=False)
            st.bar_chart(size_df.set_index("Cluster")["Size"])

        st.markdown("#### Impression Distribution")
        if ads_df is not None and "impression_mid" in ads_df.columns:
            imp_data = ads_df["impression_mid"].replace(0, None).dropna()
            if not imp_data.empty:
                bins = pd.cut(imp_data, bins=10)
                st.bar_chart(bins.value_counts().sort_index())
        elif cluster_data:
            imp_df = pd.DataFrame(
                [
                    {
                        "Cluster": f"C{c['cluster_id']}",
                        "Avg Impressions": c["avg_impression_mid"],
                    }
                    for c in cluster_data
                ]
            ).sort_values("Avg Impressions", ascending=False)
            st.bar_chart(imp_df.set_index("Cluster")["Avg Impressions"])

    with col_v2:
        st.markdown("#### Winner Score by Cluster")
        if cluster_data:
            score_df = pd.DataFrame(
                [
                    {
                        "Cluster": f"C{c['cluster_id']} ({c['angle_type']})",
                        "Winner Score": c["avg_winner_score"],
                    }
                    for c in cluster_data
                ]
            ).sort_values("Winner Score", ascending=False)
            st.bar_chart(score_df.set_index("Cluster")["Winner Score"])

        st.markdown("#### UMAP 2D Cluster Map")
        if umap_2d is not None and ads_df is not None and "cluster_id" in ads_df.columns:
            try:
                n = min(len(umap_2d), len(ads_df))
                scatter_df = pd.DataFrame(
                    {
                        "x": umap_2d[:n, 0],
                        "y": umap_2d[:n, 1],
                        "cluster": ads_df["cluster_id"].values[:n].astype(str),
                    }
                )
                st.scatter_chart(scatter_df, x="x", y="y", color="cluster")
            except Exception as e:
                st.info(f"Could not render UMAP scatter: {e}")
        else:
            st.info(
                "UMAP 2D visualisation requires a full run with UMAP enabled. "
                "Re-run with 'Use UMAP' toggled on."
            )

# ------------------------------------------------------------------ #
# Footer
# ------------------------------------------------------------------ #

st.markdown("---")
st.caption(
    "Creative Intelligence Dashboard · Built with Playwright + sentence-transformers + HDBSCAN · "
    "No API keys required · Public data only"
)
