# Africa Gender Violence Index (GVI)

Ngorima, T. & Moyo, E. (2024). Africa Gender Violence Index (GVI): A Composite Indicator Framework.

## Overview

The Africa Gender Violence Index (GVI) is a diagnostic composite indicator developed to surface
structural patterns of gender-based violence across all 55 African Union member states. It focuses
on six non-substitutable pillars: Sexual, Physical, Psychological, Economic, Environmental and
Emotional violence. Higher scores indicate a worse gender violence environment.

## Conceptual Framework

| Pillar | Definition |
|--------|-----------|
| Sexual | Rape, sexual assault, coerced sex, marital rape |
| Physical | Intimate partner physical violence and non-partner assault |
| Psychological | Emotional abuse, controlling behaviours, threats |
| Economic | Denial of economic resources, property rights violations |
| Environmental | Climate displacement impacts on women's safety |
| Emotional | Verbal abuse, humiliation, isolation |

## Methodology

- **Simulation:** Prevalence-style simulated indicators using truncated normal distributions and
  regional offsets.
- **Normalization:** Exogenous min-max with theoretical bounds (0–70) per OECD §4.
- **Aggregation:** Weighted geometric mean across pillars to enforce non-substitutability (OECD §5).

## Non-Substitutability Rationale

The geometric mean penalises extreme imbalance across pillars — a country cannot compensate very
high levels in one pillar by low levels in another. This aligns with OECD guidance on
non-substitutable dimensions.

---

## Project Structure

```
gender_index/
├── main.py                   # Pipeline entry point (generates all CSV/map outputs)
├── dashboard.py              # Interactive Streamlit dashboard
├── requirements.txt          # Python dependencies
├── README.md
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── constants.py          # AU member states, pillar specs, weighting scenarios
│   ├── data_generator.py     # Truncated-normal simulation with regional offsets
│   ├── gvi_model.py          # Min-max normalisation + weighted geometric mean
│   ├── sensitivity.py        # Diagnostics, Spearman stability, z-score outliers
│   └── visualization.py      # Choropleth maps, shapefiles, bar charts
├── tests/
│   └── test_gvi.py
├── data/                     # Auto-downloaded shapefiles cache
├── outputs/                  # Generated CSVs and PNG maps (git-ignored)
└── shapefiles/               # Generated GeoPackage and Shapefile exports (git-ignored)
```

---

## Installation & Usage

### 1. Set up the environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Run the data pipeline

Generates all CSVs, PNG maps, and shapefiles into `outputs/` and `shapefiles/`:

```bash
python main.py
```

### 3. Launch the interactive dashboard

```bash
streamlit run dashboard.py
```

The dashboard opens at **http://localhost:8501** in your browser.

To share on your local network (same Wi-Fi):

```bash
streamlit run dashboard.py --server.address 0.0.0.0
```

Then share: **http://YOUR_IP_ADDRESS:8501**

---

## Dashboard Features

| Tab | Description |
|-----|-------------|
| 🗺️ Map | Interactive choropleth — overall GVI and individual pillars |
| 📊 Rankings | Top/bottom country bar charts + full sortable data table |
| 🔬 Pillar Analysis | Heatmap, correlation matrix, regional averages |
| 🔍 Country Profile | Radar chart vs Africa average + scenario comparison |
| 📉 Sensitivity | Spearman rank-stability heatmap + max rank shifts |
| 📋 Diagnostics | Distribution statistics + raw pillar box plots |

---

## Outputs

| File | Description |
|------|-------------|
| `outputs/01_raw_data.csv` | Raw simulated prevalence (%) per pillar |
| `outputs/02_gvi_ranked.csv` | GVI scores and rankings (1 = worst) |
| `outputs/03_pillar_breakdown.csv` | Normalized pillar scores |
| `outputs/04_sensitivity_scenarios.csv` | Scores & ranks across all scenarios |
| `outputs/05_correlation_matrix.csv` | Pearson correlation matrix |
| `outputs/06_distribution_diagnostics.csv` | mean, std, skew, kurtosis, Shapiro-Wilk |
| `outputs/07_zscore_outliers.csv` | Countries with \|z\| > 2.5 on any pillar |
| `outputs/08_rank_stability_spearman.csv` | Spearman ρ between scenarios |
| `outputs/09_rank_shifts.csv` | Max rank displacement per country |
| `outputs/gvi_overall.png` | High-res overall GVI choropleth |
| `outputs/gvi_*_map.png` | High-res per-pillar choropleths |
| `outputs/gvi_rank_barchart.png` | Top/bottom 15 countries bar chart |
| `shapefiles/africa_gvi.shp` | ESRI Shapefile with GVI data |
| `shapefiles/africa_gvi.gpkg` | GeoPackage with GVI data |

---

## Sensitivity Analysis

Four weighting scenarios:

| Scenario | Description |
|----------|-------------|
| Baseline | Equal weights (1/6 each) |
| A — Psychological focus | Psychological = 0.40, others reduced |
| B — Economic focus | Economic = 0.40, others reduced |
| C — Physical focus | Physical = 0.40, others reduced |

Spearman correlations between scenario rankings measure robustness; **ρ > 0.85** indicates
robust rank order.

---

## Limitations

- Data are **simulated** for demonstrative purposes only and should not be interpreted as real
  prevalence estimates.
- Single indicator per pillar reduces within-pillar richness.
- Environmental violence is an emerging measurement domain and is modelled heuristically.

---

## References

- OECD (2008). *Handbook on Constructing Composite Indicators.*
- WHO (2021). *Violence against women.*
- DHS Program.
- UNFPA (2023).
- Alkire, S. & Foster, J. (2011).
