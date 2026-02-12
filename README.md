# Africa Gender Violence Index (GVI)

Ngorima, T. & Moyo, E. (2024). Africa Gender Violence Index (GVI): A Composite Indicator Framework.

Overview
--------
The Africa Gender Violence Index (GVI) is a diagnostic composite indicator developed to surface structural patterns of gender-based violence across all 55 African Union member states. It focuses on six non-substitutable pillars: Sexual, Physical, Psychological, Economic, Environmental and Emotional violence. Higher scores indicate a worse gender violence environment.

Conceptual Framework
--------------------
- Sexual Violence: rape, sexual assault, coerced sex, marital rape.
- Physical Violence: intimate partner physical violence and non-partner assault.
- Psychological Violence: emotional abuse, controlling behaviours, threats.
- Economic Violence: denial of economic resources, property rights violations.
- Environmental Violence: climate displacement impacts on women's safety.
- Emotional Violence: verbal abuse, humiliation, isolation.

Methodology
-----------
- Simulation: prevalence-style simulated indicators using truncated normal distributions and regional offsets.
- Normalization: exogenous min-max with theoretical bounds (0–70) per OECD §4.
- Aggregation: weighted geometric mean across pillars to enforce non-substitutability (OECD §5).

Non-Substitutability Rationale
------------------------------
The geometric mean penalises extreme imbalance across pillars — a country cannot compensate very high levels in one pillar by low levels in another. This aligns with OECD guidance on non-substitutable dimensions.

Project Structure
-----------------
gvi_project/
├── main.py
├── requirements.txt
├── README.md
├── src/
│   ├── __init__.py
│   ├── constants.py
│   ├── data_generator.py
│   ├── gvi_model.py
│   ├── sensitivity.py
│   └── visualization.py
├── tests/
│   └── test_gvi.py
├── data/
├── outputs/
└── shapefiles/

Installation & Usage
---------------------
1. Create and activate a Python 3.11+ virtual environment.

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
python main.py
```

VS Code Instructions
--------------------
- Open the folder in VS Code.
- Select the interpreter from the `.venv` created above.
- Run `main.py` (F5) or via the terminal.

Outputs
-------
- `outputs/01_raw_data.csv`: Raw simulated prevalence (%) per pillar
- `outputs/02_gvi_ranked.csv`: GVI scores and rankings (1 = worst)
- `outputs/03_pillar_breakdown.csv`: Normalized pillar scores
- `outputs/04_sensitivity_scenarios.csv`: Scores & ranks across scenarios
- `outputs/05_correlation_matrix.csv`: Pearson correlation matrix
- `outputs/06_distribution_diagnostics.csv`: mean,std,skew,kurt,Shapiro-Wilk
- `outputs/07_zscore_outliers.csv`: Countries with |z|>2.5 on any pillar
- `outputs/08_rank_stability_spearman.csv`: Spearman rho between scenarios
- `outputs/09_rank_shifts.csv`: Max rank displacement per country
- PNG maps: high-resolution choropleths for overall GVI and each pillar
- Shapefiles in `shapefiles/`: `africa_gvi.shp` and `africa_gvi.gpkg`

Sensitivity Analysis
--------------------
Four weighting scenarios are used: Baseline (equal), Psychological focus, Economic focus, Physical focus. Spearman correlations between scenario rankings measure robustness; ρ>0.85 indicates robust rank order.

Limitations
-----------
- Data are simulated for demonstrative purposes only and should not be interpreted as real prevalence estimates.
- Single indicator per pillar reduces within-pillar richness.
- Environmental violence is an emerging measurement domain and is modeled heuristically.

References
----------
- OECD (2008). Handbook on Constructing Composite Indicators.
- WHO (2021). Violence against women.
- DHS Program.
- UNFPA (2023).
- Alkire, S. & Foster, J. (2011).
