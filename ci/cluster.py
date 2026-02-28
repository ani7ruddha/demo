"""
Clustering module.

Clusters ad embeddings using HDBSCAN (preferred) or KMeans (fallback).
For each cluster, computes:
  - size
  - avg/median impression_mid
  - avg winner_score (populated later by score.py)
  - top-5 TF-IDF keywords
  - medoid (most representative ad)
  - angle type (populated later by insights.py)
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CLEAN_INPUT = DATA_DIR / "ads_clean.jsonl"
EMBEDDINGS_INPUT = DATA_DIR / "embeddings.npy"
CLUSTERS_OUTPUT = DATA_DIR / "clusters.json"
ADS_WITH_CLUSTERS = DATA_DIR / "ads_clustered.jsonl"

# Minimum cluster size for HDBSCAN
MIN_CLUSTER_SIZE = 3


# ---------------------------------------------------------------------------
# Clustering algorithms
# ---------------------------------------------------------------------------

def _hdbscan_cluster(embeddings: np.ndarray, min_cluster_size: int) -> np.ndarray:
    """Run HDBSCAN; returns integer label array (-1 = noise)."""
    try:
        import hdbscan  # type: ignore

        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=min_cluster_size,
            metric="euclidean",
            cluster_selection_method="eom",
        )
        return clusterer.fit_predict(embeddings)
    except ImportError:
        print("[WARN] hdbscan not available. Falling back to KMeans.")
        return None  # type: ignore


def _kmeans_cluster(embeddings: np.ndarray, n_clusters: int | None = None) -> np.ndarray:
    """Run KMeans with automatic k selection via silhouette."""
    from sklearn.cluster import KMeans  # type: ignore
    from sklearn.metrics import silhouette_score  # type: ignore

    n = embeddings.shape[0]
    if n_clusters is None:
        # Try k = 3..min(15, n//3) and pick best silhouette
        best_k, best_score = 3, -1.0
        for k in range(3, min(16, n // 2 + 1)):
            km = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = km.fit_predict(embeddings)
            try:
                s = silhouette_score(embeddings, labels, sample_size=min(500, n))
                if s > best_score:
                    best_score, best_k = s, k
            except Exception:
                pass
        n_clusters = best_k

    print(f"[INFO] KMeans with k={n_clusters}")
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    return km.fit_predict(embeddings)


def cluster_embeddings(
    embeddings: np.ndarray,
    min_cluster_size: int = MIN_CLUSTER_SIZE,
) -> np.ndarray:
    """
    Cluster embeddings; returns integer label array.
    Noise points (-1) from HDBSCAN are assigned to a pseudo-cluster.
    """
    n = embeddings.shape[0]
    if n < 4:
        return np.zeros(n, dtype=int)

    labels = _hdbscan_cluster(embeddings, min_cluster_size)
    if labels is None:
        labels = _kmeans_cluster(embeddings)

    # Re-assign noise points to nearest real cluster (or their own group)
    unique_real = [l for l in np.unique(labels) if l >= 0]
    if unique_real and np.any(labels == -1):
        from sklearn.neighbors import NearestNeighbors  # type: ignore

        real_mask = labels >= 0
        nn = NearestNeighbors(n_neighbors=1).fit(embeddings[real_mask])
        noise_idx = np.where(labels == -1)[0]
        _, neighbors = nn.kneighbors(embeddings[noise_idx])
        real_indices = np.where(real_mask)[0]
        for i, ni in zip(noise_idx, neighbors[:, 0]):
            labels[i] = labels[real_indices[ni]]

    return labels.astype(int)


# ---------------------------------------------------------------------------
# TF-IDF keywords per cluster
# ---------------------------------------------------------------------------

def top_keywords(texts: list[str], n: int = 5) -> list[str]:
    """Extract top-n TF-IDF keywords from a list of texts."""
    if not texts:
        return []
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore

        vec = TfidfVectorizer(
            max_features=500,
            stop_words="english",
            ngram_range=(1, 2),
        )
        X = vec.fit_transform(texts)
        scores = np.asarray(X.sum(axis=0)).ravel()
        top_idx = scores.argsort()[-n:][::-1]
        feature_names = vec.get_feature_names_out()
        return [feature_names[i] for i in top_idx]
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Medoid selection
# ---------------------------------------------------------------------------

def find_medoid(embeddings: np.ndarray, indices: list[int]) -> int:
    """Return the index (within embeddings) of the medoid."""
    sub = embeddings[indices]
    # Pairwise cosine distances
    norms = np.linalg.norm(sub, axis=1, keepdims=True) + 1e-9
    sub_norm = sub / norms
    sim = sub_norm @ sub_norm.T
    # Medoid = row with highest average similarity
    avg_sim = sim.mean(axis=1)
    return indices[int(np.argmax(avg_sim))]


# ---------------------------------------------------------------------------
# Build cluster summary
# ---------------------------------------------------------------------------

def build_clusters(
    ads: list[dict[str, Any]],
    labels: np.ndarray,
    embeddings: np.ndarray,
) -> dict[int, dict[str, Any]]:
    """
    Build per-cluster summary dicts.
    Returns mapping cluster_id → summary.
    """
    cluster_indices: dict[int, list[int]] = defaultdict(list)
    for idx, label in enumerate(labels):
        cluster_indices[int(label)].append(idx)

    clusters: dict[int, dict[str, Any]] = {}

    for cid, idxs in cluster_indices.items():
        cluster_ads = [ads[i] for i in idxs]
        texts = [a.get("creative_text") or a.get("ad_body") or "" for a in cluster_ads]
        imp_mids = [a.get("impression_mid", 0.0) for a in cluster_ads]

        medoid_global_idx = find_medoid(embeddings, idxs)
        rep_ad = ads[medoid_global_idx]

        clusters[cid] = {
            "cluster_id": cid,
            "size": len(idxs),
            "indices": idxs,
            "avg_impression_mid": float(np.mean(imp_mids)) if imp_mids else 0.0,
            "median_impression_mid": float(np.median(imp_mids)) if imp_mids else 0.0,
            "max_impression_mid": float(np.max(imp_mids)) if imp_mids else 0.0,
            "top_keywords": top_keywords(texts, n=5),
            "medoid_index": medoid_global_idx,
            "representative_ad": rep_ad,
            "angle_type": "",       # filled by insights.py
            "winner_score": 0.0,    # filled by score.py
            "avg_winner_score": 0.0,  # filled by score.py
        }

    return clusters


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_clustering(
    ads: list[dict[str, Any]] | None = None,
    embeddings: np.ndarray | None = None,
    min_cluster_size: int = MIN_CLUSTER_SIZE,
) -> tuple[dict[int, dict[str, Any]], np.ndarray]:
    """
    Run the full clustering pipeline.

    If ads/embeddings not provided, loads from disk.
    Returns (clusters_dict, labels_array).
    """
    if ads is None:
        ads = []
        with CLEAN_INPUT.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    ads.append(json.loads(line))

    if embeddings is None:
        embeddings = np.load(EMBEDDINGS_INPUT)

    print(f"[INFO] Clustering {len(ads)} ads with min_cluster_size={min_cluster_size}")
    labels = cluster_embeddings(embeddings, min_cluster_size)
    unique_labels = np.unique(labels)
    print(f"[INFO] Found {len(unique_labels)} clusters: {unique_labels.tolist()}")

    clusters = build_clusters(ads, labels, embeddings)

    # Attach cluster_id to each ad
    for idx, (ad, label) in enumerate(zip(ads, labels)):
        ad["cluster_id"] = int(label)

    # Save updated ads
    with ADS_WITH_CLUSTERS.open("w", encoding="utf-8") as f:
        for ad in ads:
            f.write(json.dumps(ad, ensure_ascii=False) + "\n")

    # Save cluster summaries
    clusters_serializable = {
        str(k): v for k, v in clusters.items()
    }
    # Remove non-serializable 'indices' list (large), keep as-is (it's ints)
    with CLUSTERS_OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(clusters_serializable, f, indent=2, ensure_ascii=False)

    print(f"[INFO] Clusters saved → {CLUSTERS_OUTPUT}")
    return clusters, labels


if __name__ == "__main__":
    run_clustering()
