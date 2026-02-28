# Creative Intelligence Dashboard

Automated Meta Ads Library analyser that scrapes public ad creatives via Playwright browser automation, clusters them by creative similarity, scores them by impression signal, and surfaces winning angles in a Streamlit dashboard.

**No API keys required.** Public ad data only.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Meta Ads Library (browser)                             │
│           │  Playwright                                 │
│           ▼                                             │
│   ci/ingest_playwright.py  →  data/ads_raw.jsonl        │
│           │                                             │
│   ci/extract.py            →  data/ads_extracted.jsonl  │
│           │                                             │
│   ci/clean.py              →  data/ads_clean.jsonl      │
│           │                                             │
│   ci/embed.py              →  data/embeddings.npy       │
│           │                   data/umap_2d.npy          │
│           │                                             │
│   ci/cluster.py            →  data/clusters.json        │
│           │                   data/ads_clustered.jsonl  │
│           │                                             │
│   ci/score.py              →  data/ads_scored.jsonl     │
│           │                   data/clusters_scored.json │
│           │                                             │
│   ci/insights.py           →  data/insights.json        │
│                                data/insights.md         │
│                                                         │
│   app/dashboard.py  ←── Streamlit UI                    │
└─────────────────────────────────────────────────────────┘
```

### Stack

| Layer | Library |
|---|---|
| Browser automation | Playwright (Chromium) |
| HTML parsing | BeautifulSoup 4 |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Dimensionality reduction | UMAP (fallback: PCA) |
| Clustering | HDBSCAN (fallback: KMeans) |
| Keyword extraction | scikit-learn TF-IDF |
| Dashboard | Streamlit |

---

## Quick Start

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Playwright browsers

```bash
playwright install chromium
```

### 3. (Optional) Copy environment config

```bash
cp .env.example .env
```

### 4. Run the pipeline (CLI)

```bash
python -m ci.pipeline \
  --url "https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=US&q=fitness&search_type=keyword_unordered" \
  --max_ads 300 \
  --headless false
```

### 5. Launch the dashboard

```bash
streamlit run app/dashboard.py
```

Then open `http://localhost:8501` in your browser.

---

## CLI Reference

```
python -m ci.pipeline [OPTIONS]

Options:
  --url TEXT              Meta Ads Library URL to scrape  [required]
  --max_ads INT           Maximum ads to collect (default: 300)
  --headless BOOL         Run browser headless true/false (default: true)
  --skip_ingest           Reuse existing ads_raw.jsonl (skip browser step)
  --no_umap               Disable UMAP (use raw embeddings for clustering)
  --min_cluster_size INT  Minimum HDBSCAN cluster size (default: 3)
```

---

## Project Structure

```
/app
  dashboard.py          Streamlit dashboard UI

/ci
  __init__.py
  ingest_playwright.py  Playwright browser scraper
  extract.py            HTML → structured fields
  clean.py              Normalization + impression parsing
  embed.py              Sentence-transformer embeddings + UMAP
  cluster.py            HDBSCAN / KMeans clustering
  score.py              Winner score + saturation index
  insights.py           Angle classification + report generation
  pipeline.py           End-to-end orchestrator + CLI

/data                   Generated data files (gitignored)
  ads_raw.jsonl
  ads_extracted.jsonl
  ads_clean.jsonl
  embeddings.npy
  umap_2d.npy
  ads_clustered.jsonl
  clusters.json
  ads_scored.jsonl
  clusters_scored.json
  insights.json
  insights.md

.env.example            Environment variable template
requirements.txt        Python dependencies
```

---

## How It Works

### Ingestion
Playwright launches a Chromium browser, navigates to the Ads Library URL, and scrolls until `max_ads` ad cards are loaded (or 3 consecutive scroll attempts yield no new cards). It optionally attempts to sort by "Highest impressions" if the dropdown is available. Raw card HTML is saved to `data/ads_raw.jsonl`.

Scrolling uses a randomised 1.5–3 second delay to respect rate limits.

### Extraction
BeautifulSoup parses each card's HTML to pull: advertiser name, ad body, headline, CTA, impression range, start date, platform icons, and thumbnail URL.

The CSS selector map is configured in `ci/ingest_playwright.py → SELECTORS`. If Meta changes the DOM, update the selectors there.

### Normalization
Impression strings like "10K–50K impressions" are parsed into `impression_lower`, `impression_upper`, and `impression_mid`. Start dates are normalised to `YYYY-MM-DD`. Longevity (days running) is computed from today's date.

### Winner Score
```
winner_score = log(impression_mid + 1)
             + log(longevity_days + 1)
             + cluster_density_weight
```

`cluster_density_weight` = normalised log of the cluster's average impression mid, scaled 0–2.

### Clustering
Texts are embedded with `all-MiniLM-L6-v2`, optionally reduced with UMAP, then clustered with HDBSCAN. Noise points are assigned to their nearest real cluster. Each cluster gets TF-IDF keyword extraction and a medoid representative ad.

### Angle Classification
Clusters are classified into 9 creative angles (Authority, Fear, Aspiration, Savings, Convenience, Mechanism, Social Proof, Curiosity, Urgency) via keyword matching on the representative ad text.

### Saturation Index
The Herfindahl–Hirschman Index (HHI) measures market concentration across clusters:
- `< 0.15` → fragmented, many opportunities
- `0.15–0.35` → moderate concentration
- `> 0.35` → high saturation, few angles dominate

### Scalable Clusters (Bonus)
Clusters where `avg_impression_mid > median` AND `avg_longevity_days > median` AND `size > 3` are flagged as "likely winning themes".

---

## Dashboard Features

| Section | Description |
|---|---|
| KPI Row | Total ads, clusters, saturation score, avg winner score |
| Overview | Angle distribution bar chart, underserved opportunities, winning themes |
| Cluster Table | All clusters ranked by winner score, styled with gold for scalable clusters |
| Cluster Detail | Representative ad, top keywords, all ads in cluster |
| Top Hooks | Top 20 opening phrases from highest-scoring ads |
| Visualisations | Cluster sizes, impression distribution, winner score chart, UMAP 2D scatter |

---

## Troubleshooting

### No ads found after scraping
- Try `--headless false` to see what the browser is loading
- The Ads Library may require accepting cookies — run headful once to set state
- Check `ci/ingest_playwright.py → SELECTORS["ad_card"]` against the live DOM
- Print the first card HTML by temporarily adding `print(page.inner_html("body")[:3000])` in `ingest_playwright.py`

### HDBSCAN produces too many noise points
- Lower `--min_cluster_size` to 2
- Disable UMAP with `--no_umap` and cluster on raw embeddings

### sentence-transformers not available
- The system automatically falls back to TF-IDF + SVD embeddings
- Install: `pip install sentence-transformers`

### UMAP not available
- The system automatically falls back to PCA
- Install: `pip install umap-learn`

---

## Limitations

- Only collects **publicly visible** ad data from the Meta Ads Library
- Impression ranges are approximate buckets, not exact figures
- Start dates are not always shown for all ads
- Meta may update their DOM — selectors in `SELECTORS` dict may need updating
- Browser fingerprinting may limit how many ads load per session

---

## Ethics & Legal

- Only scrapes publicly accessible data from `facebook.com/ads/library`
- Does not bypass authentication, paywalls, or rate limits
- Includes randomised delays to avoid overloading servers
- Use responsibly and in compliance with Meta's Terms of Service
