"""
Embedding module.

Generates sentence embeddings for ad creative_text using
sentence-transformers/all-MiniLM-L6-v2 and optionally reduces
dimensionality with UMAP before clustering.

Outputs:
  data/embeddings.npy   — (N, D) float32 array
  data/umap_2d.npy      — (N, 2) float32 for visualisation (optional)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CLEAN_INPUT = DATA_DIR / "ads_clean.jsonl"
EMBEDDINGS_OUTPUT = DATA_DIR / "embeddings.npy"
UMAP_OUTPUT = DATA_DIR / "umap_2d.npy"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


# ---------------------------------------------------------------------------
# Load ads
# ---------------------------------------------------------------------------

def load_clean_ads(path: Path = CLEAN_INPUT) -> list[dict[str, Any]]:
    records = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


# ---------------------------------------------------------------------------
# Embedding
# ---------------------------------------------------------------------------

def embed_texts(texts: list[str], model_name: str = MODEL_NAME) -> np.ndarray:
    """
    Encode a list of strings → (N, D) float32 numpy array.
    Falls back to TF-IDF if sentence-transformers is unavailable.
    """
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore

        print(f"[INFO] Loading embedding model: {model_name}")
        model = SentenceTransformer(model_name)
        embeddings = model.encode(
            texts,
            batch_size=64,
            show_progress_bar=True,
            convert_to_numpy=True,
        )
        return embeddings.astype(np.float32)
    except ImportError:
        print("[WARN] sentence-transformers not available. Falling back to TF-IDF.")
        return _tfidf_embed(texts)


def _tfidf_embed(texts: list[str]) -> np.ndarray:
    """Sparse TF-IDF fallback — returns dense float32 matrix."""
    from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
    from sklearn.decomposition import TruncatedSVD  # type: ignore

    vec = TfidfVectorizer(max_features=512, sublinear_tf=True)
    X_sparse = vec.fit_transform(texts)
    n_components = min(64, X_sparse.shape[1] - 1, X_sparse.shape[0] - 1)
    if n_components < 2:
        return X_sparse.toarray().astype(np.float32)
    svd = TruncatedSVD(n_components=n_components, random_state=42)
    return svd.fit_transform(X_sparse).astype(np.float32)


# ---------------------------------------------------------------------------
# UMAP reduction
# ---------------------------------------------------------------------------

def reduce_umap(
    embeddings: np.ndarray,
    n_components: int = 10,
    n_components_2d: int = 2,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Reduce to n_components for clustering and n_components_2d for plotting.
    Returns (reduced_for_cluster, reduced_2d).
    Falls back to PCA if umap-learn is unavailable.
    """
    if embeddings.shape[0] < 5:
        # Not enough data to reduce meaningfully
        return embeddings, embeddings[:, :2] if embeddings.shape[1] >= 2 else embeddings

    try:
        import umap  # type: ignore

        print(f"[INFO] UMAP reduction → {n_components}d (cluster) + 2d (plot).")
        reducer_nd = umap.UMAP(
            n_components=n_components,
            metric="cosine",
            random_state=42,
            n_jobs=1,
        )
        reduced = reducer_nd.fit_transform(embeddings)

        reducer_2d = umap.UMAP(
            n_components=n_components_2d,
            metric="cosine",
            random_state=42,
            n_jobs=1,
        )
        reduced_2d = reducer_2d.fit_transform(embeddings)
        return reduced.astype(np.float32), reduced_2d.astype(np.float32)

    except ImportError:
        print("[WARN] umap-learn not available. Falling back to PCA.")
        from sklearn.decomposition import PCA  # type: ignore

        n_components = min(n_components, embeddings.shape[1], embeddings.shape[0] - 1)
        pca_nd = PCA(n_components=n_components, random_state=42)
        reduced = pca_nd.fit_transform(embeddings)

        pca_2d = PCA(n_components=min(2, embeddings.shape[1]), random_state=42)
        reduced_2d = pca_2d.fit_transform(embeddings)
        return reduced.astype(np.float32), reduced_2d.astype(np.float32)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_embeddings(
    input_path: Path = CLEAN_INPUT,
    embeddings_path: Path = EMBEDDINGS_OUTPUT,
    umap_path: Path = UMAP_OUTPUT,
    use_umap: bool = True,
) -> tuple[np.ndarray, np.ndarray, list[dict[str, Any]]]:
    """
    Load clean ads, embed, optionally reduce, and save arrays.

    Returns (embeddings_for_clustering, umap_2d, ads_list)
    """
    ads = load_clean_ads(input_path)
    if not ads:
        raise ValueError(f"No ads found in {input_path}")

    texts = [ad.get("creative_text") or ad.get("ad_body") or "" for ad in ads]
    # Replace empty texts with a placeholder
    texts = [t if t.strip() else "(no text)" for t in texts]

    raw_embeddings = embed_texts(texts)
    print(f"[INFO] Raw embeddings shape: {raw_embeddings.shape}")

    if use_umap and raw_embeddings.shape[0] >= 5:
        cluster_embeddings, umap_2d = reduce_umap(raw_embeddings)
    else:
        cluster_embeddings = raw_embeddings
        umap_2d = raw_embeddings[:, :2] if raw_embeddings.shape[1] >= 2 else raw_embeddings

    np.save(embeddings_path, cluster_embeddings)
    np.save(umap_path, umap_2d)
    print(f"[INFO] Embeddings saved → {embeddings_path}")
    print(f"[INFO] UMAP 2d saved   → {umap_path}")

    return cluster_embeddings, umap_2d, ads


if __name__ == "__main__":
    run_embeddings()
