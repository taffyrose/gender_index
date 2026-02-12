"""Streamlit dashboard for the Africa Gender Violence Index (GVI).

Run with:
    streamlit run dashboard.py

Shareable link (local network):
    streamlit run dashboard.py --server.address 0.0.0.0
"""
import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Africa Gender Violence Index (GVI)",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

PILLAR_COLS = ["Sexual", "Physical", "Psychological", "Economic", "Environmental", "Emotional"]
NORM_COLS   = [f"{p}_Norm" for p in PILLAR_COLS]
REGION_COLORS = {
    "North":    "#1f77b4",
    "West":     "#ff7f0e",
    "Central":  "#d62728",
    "East":     "#2ca02c",
    "Southern": "#9467bd",
}

# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Running GVI pipeline…")
def load_data() -> dict:
    """Load CSV outputs, running the pipeline first if outputs are missing."""
    needed = [
        "outputs/01_raw_data.csv",
        "outputs/02_gvi_ranked.csv",
        "outputs/03_pillar_breakdown.csv",
        "outputs/04_sensitivity_scenarios.csv",
        "outputs/05_correlation_matrix.csv",
        "outputs/06_distribution_diagnostics.csv",
        "outputs/08_rank_stability_spearman.csv",
        "outputs/09_rank_shifts.csv",
    ]
    if not all(os.path.exists(f) for f in needed):
        from src.data_generator import generate_base_countries, simulate_pillars
        from src.gvi_model import normalize_pillars, compute_gvi_for_scenarios
        from src.sensitivity import run_sensitivity_and_diagnostics
        os.makedirs("outputs", exist_ok=True)
        os.makedirs("data", exist_ok=True)
        os.makedirs("shapefiles", exist_ok=True)
        countries_df = generate_base_countries()
        raw_df = simulate_pillars(countries_df)
        norm_df = normalize_pillars(raw_df)
        all_results = compute_gvi_for_scenarios(norm_df)
        run_sensitivity_and_diagnostics(all_results)

    return {
        "raw":        pd.read_csv("outputs/01_raw_data.csv"),
        "ranked":     pd.read_csv("outputs/02_gvi_ranked.csv"),
        "pillars":    pd.read_csv("outputs/03_pillar_breakdown.csv"),
        "scenarios":  pd.read_csv("outputs/04_sensitivity_scenarios.csv"),
        "corr":       pd.read_csv("outputs/05_correlation_matrix.csv", index_col=0),
        "diag":       pd.read_csv("outputs/06_distribution_diagnostics.csv"),
        "spearman":   pd.read_csv("outputs/08_rank_stability_spearman.csv", index_col=0),
        "shifts":     pd.read_csv("outputs/09_rank_shifts.csv"),
    }


data = load_data()
ranked     = data["ranked"]
raw        = data["raw"]
pillars_df = data["pillars"]
scenarios  = data["scenarios"]
corr       = data["corr"]
diag       = data["diag"]
spearman   = data["spearman"]
shifts     = data["shifts"]

# Merge pillars into ranked for full table
full = ranked.merge(
    pillars_df[["Country", "ISO3"] + NORM_COLS],
    on=["Country", "ISO3"],
    how="left",
).merge(
    raw[["Country", "ISO3"] + PILLAR_COLS],
    on=["Country", "ISO3"],
    how="left",
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("🌍 GVI Explorer")
st.sidebar.markdown("**Africa Gender Violence Index**")
st.sidebar.markdown("Ngorima & Moyo (2024) — Simulated Data")
st.sidebar.divider()

regions = ["All"] + sorted(full["Region"].unique().tolist())
sel_region = st.sidebar.selectbox("Filter by Region", regions)

n_top = st.sidebar.slider("Countries shown in charts", 10, 55, 20)

scenario_labels = {
    "baseline":      "Baseline (equal weights)",
    "A_psych_focus": "Scenario A — Psychological focus",
    "B_econ_focus":  "Scenario B — Economic focus",
    "C_phys_focus":  "Scenario C — Physical focus",
}
sel_scenario = st.sidebar.selectbox(
    "Weighting Scenario",
    list(scenario_labels.keys()),
    format_func=lambda k: scenario_labels[k],
)
st.sidebar.divider()
st.sidebar.info(
    "Higher GVI score = worse gender violence environment.  \n"
    "Score range: 0 (best) → 1 (worst)."
)

# Apply region filter
disp = full.copy()
if sel_region != "All":
    disp = disp[disp["Region"] == sel_region]

score_col = f"GVI_{sel_scenario}_Score" if sel_scenario != "baseline" else "GVI_Score"
rank_col  = f"GVI_{sel_scenario}_Rank"  if sel_scenario != "baseline" else "GVI_Rank"

if sel_scenario != "baseline":
    scen_cols = scenarios[["Country", "ISO3", score_col, rank_col]].copy()
    disp = disp.drop(columns=["GVI_Score", "GVI_Rank"], errors="ignore").merge(
        scen_cols, on=["Country", "ISO3"], how="left"
    )
    disp = disp.rename(columns={score_col: "GVI_Score", rank_col: "GVI_Rank"})

disp = disp.sort_values("GVI_Rank")

# ── Header ────────────────────────────────────────────────────────────────────
st.title("Africa Gender Violence Index (GVI)")
st.caption(
    "A composite indicator across 6 pillars for 55 African Union member states. "
    "**Data are simulated for demonstrative purposes.**"
)

# ── KPI row ───────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
worst_row  = disp.iloc[0]
best_row   = disp.iloc[-1]
avg_score  = disp["GVI_Score"].mean()
n_countries = len(disp)

k1.metric("Countries shown", n_countries)
k2.metric("Avg GVI Score", f"{avg_score:.3f}")
k3.metric("Highest GVI (worst)", worst_row["Country"], f"{worst_row['GVI_Score']:.3f}")
k4.metric("Lowest GVI (best)",   best_row["Country"],  f"{best_row['GVI_Score']:.3f}")
k5.metric("Scenario", scenario_labels[sel_scenario].split("—")[-1].strip())

st.divider()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_map, tab_rank, tab_pillar, tab_country, tab_sensitivity, tab_diag = st.tabs([
    "🗺️ Map", "📊 Rankings", "🔬 Pillar Analysis",
    "🔍 Country Profile", "📉 Sensitivity", "📋 Diagnostics"
])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 1 — MAP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_map:
    map_metric = st.selectbox(
        "Map metric",
        ["GVI_Score"] + NORM_COLS,
        format_func=lambda c: c.replace("_Norm", " (normalized)").replace("_", " "),
    )

    map_df = full.copy()
    if sel_scenario != "baseline" and map_metric == "GVI_Score":
        map_df = map_df.drop(columns=["GVI_Score", "GVI_Rank"], errors="ignore").merge(
            scenarios[["Country", "ISO3", score_col, rank_col]],
            on=["Country", "ISO3"], how="left"
        ).rename(columns={score_col: "GVI_Score", rank_col: "GVI_Rank"})

    fig_map = px.choropleth(
        map_df,
        locations="ISO3",
        color=map_metric,
        hover_name="Country",
        hover_data={"Region": True, "GVI_Score": ":.3f", "GVI_Rank": True, "ISO3": False},
        color_continuous_scale="YlOrRd",
        range_color=(0, 1),
        scope="africa",
        title=f"Africa GVI — {map_metric.replace('_Norm',' (normalized)').replace('_',' ')}",
        labels={map_metric: map_metric.replace("_Norm", "").replace("_", " ")},
    )
    fig_map.update_layout(
        height=600,
        margin=dict(l=0, r=0, t=40, b=0),
        coloraxis_colorbar=dict(title="Score", tickformat=".2f"),
        geo=dict(showframe=False, showcoastlines=True, bgcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig_map, use_container_width=True)
    st.caption("Light grey = no data. Hover over countries for details.")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 2 — RANKINGS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_rank:
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader(f"Top {n_top} — Highest GVI (worst)")
        top_n = disp.head(n_top).copy()
        fig_top = px.bar(
            top_n,
            x="GVI_Score", y="Country",
            orientation="h",
            color="Region",
            color_discrete_map=REGION_COLORS,
            text="GVI_Score",
            range_x=(0, 1),
        )
        fig_top.update_traces(texttemplate="%{text:.3f}", textposition="outside")
        fig_top.update_layout(height=500, yaxis={"categoryorder": "total ascending"},
                              showlegend=False, margin=dict(l=0, r=60, t=10, b=0))
        st.plotly_chart(fig_top, use_container_width=True)

    with col_right:
        st.subheader(f"Bottom {n_top} — Lowest GVI (best)")
        bot_n = disp.tail(n_top).copy()
        fig_bot = px.bar(
            bot_n,
            x="GVI_Score", y="Country",
            orientation="h",
            color="Region",
            color_discrete_map=REGION_COLORS,
            text="GVI_Score",
            range_x=(0, 1),
        )
        fig_bot.update_traces(texttemplate="%{text:.3f}", textposition="outside")
        fig_bot.update_layout(height=500, yaxis={"categoryorder": "total descending"},
                              showlegend=True, margin=dict(l=0, r=60, t=10, b=0))
        st.plotly_chart(fig_bot, use_container_width=True)

    st.subheader("Full Rankings Table")
    show_cols = ["GVI_Rank", "Country", "ISO3", "Region", "GVI_Score"] + NORM_COLS
    display_table = disp[show_cols].copy()
    display_table.columns = (
        ["Rank", "Country", "ISO3", "Region", "GVI Score"] +
        [p + " (norm)" for p in PILLAR_COLS]
    )
    st.dataframe(
        display_table.style.background_gradient(
            subset=["GVI Score"] + [p + " (norm)" for p in PILLAR_COLS],
            cmap="YlOrRd", vmin=0, vmax=1,
        ).format({
            "GVI Score": "{:.4f}",
            **{p + " (norm)": "{:.4f}" for p in PILLAR_COLS},
        }),
        use_container_width=True,
        height=500,
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 3 — PILLAR ANALYSIS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_pillar:
    st.subheader("Pillar Heatmap — Normalized Scores")
    heat_data = (
        disp.sort_values("GVI_Score")
            .set_index("Country")[NORM_COLS]
    )
    heat_data.columns = PILLAR_COLS

    fig_heat = px.imshow(
        heat_data.values,
        x=PILLAR_COLS,
        y=heat_data.index.tolist(),
        color_continuous_scale="YlOrRd",
        zmin=0, zmax=1,
        aspect="auto",
        labels=dict(x="Pillar", y="Country", color="Score"),
    )
    fig_heat.update_layout(
        height=max(400, len(heat_data) * 14),
        margin=dict(l=120, r=20, t=30, b=40),
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    st.subheader("Pillar Correlation Matrix (Pearson, raw scores)")
    fig_corr = px.imshow(
        corr,
        color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1,
        text_auto=".2f",
        aspect="auto",
    )
    fig_corr.update_layout(height=400, margin=dict(l=60, r=20, t=30, b=40))
    st.plotly_chart(fig_corr, use_container_width=True)

    st.subheader("Regional Pillar Averages")
    region_avg = (
        full.groupby("Region")[NORM_COLS]
        .mean()
        .reset_index()
    )
    region_avg.columns = ["Region"] + PILLAR_COLS
    melted = region_avg.melt(id_vars="Region", var_name="Pillar", value_name="Mean Score")
    fig_reg = px.bar(
        melted, x="Pillar", y="Mean Score", color="Region",
        barmode="group",
        color_discrete_map=REGION_COLORS,
        range_y=(0, 1),
    )
    fig_reg.update_layout(height=400, margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig_reg, use_container_width=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 4 — COUNTRY PROFILE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_country:
    country_list = sorted(full["Country"].tolist())
    sel_country = st.selectbox("Select country", country_list, index=country_list.index("South Africa"))

    row = full[full["Country"] == sel_country].iloc[0]
    scen_row = scenarios[scenarios["Country"] == sel_country].iloc[0]

    c1, c2, c3 = st.columns(3)
    c1.metric("Region",    row["Region"])
    c2.metric("GVI Score", f"{row['GVI_Score']:.4f}")
    c3.metric("GVI Rank",  f"{int(row['GVI_Rank'])} / 55")

    # Radar chart
    radar_vals = [float(row[c]) for c in NORM_COLS]
    african_avg = [float(full[c].mean()) for c in NORM_COLS]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=radar_vals + [radar_vals[0]],
        theta=PILLAR_COLS + [PILLAR_COLS[0]],
        fill="toself",
        name=sel_country,
        line_color="#d62728",
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=african_avg + [african_avg[0]],
        theta=PILLAR_COLS + [PILLAR_COLS[0]],
        fill="toself",
        name="Africa Average",
        line_color="#1f77b4",
        opacity=0.5,
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        height=420,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15),
        margin=dict(l=60, r=60, t=30, b=60),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # Scenario comparison for this country
    st.subheader("Score Across Weighting Scenarios")
    scen_data = []
    for sc_key, sc_label in scenario_labels.items():
        sc_col = f"GVI_{sc_key}_Score" if sc_key != "baseline" else "GVI_Score_x" if "GVI_Score_x" in scen_row.index else "GVI_baseline_Score"
        # Handle the baseline column name in scenarios CSV
        if sc_key == "baseline":
            sc_col = [c for c in scen_row.index if "baseline_Score" in c]
            sc_col = sc_col[0] if sc_col else "GVI_Score"
        val = float(scen_row[sc_col]) if sc_col in scen_row.index else float(row["GVI_Score"])
        rk_col = f"GVI_{sc_key}_Rank" if sc_key != "baseline" else "GVI_baseline_Rank"
        rk = int(scen_row[rk_col]) if rk_col in scen_row.index else int(row["GVI_Rank"])
        scen_data.append({"Scenario": sc_label.split("(")[-1].rstrip(")").strip(), "Score": val, "Rank": rk})
    scen_df = pd.DataFrame(scen_data)
    fig_scen = px.bar(scen_df, x="Scenario", y="Score", text="Score",
                      color="Score", color_continuous_scale="YlOrRd", range_y=(0, 1))
    fig_scen.update_traces(texttemplate="%{text:.4f}", textposition="outside")
    fig_scen.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=0),
                           coloraxis_showscale=False)
    st.plotly_chart(fig_scen, use_container_width=True)
    st.dataframe(scen_df, use_container_width=True, hide_index=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 5 — SENSITIVITY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_sensitivity:
    st.subheader("Rank Stability — Spearman ρ Between Scenarios")
    st.caption("ρ > 0.85 indicates robust rank order across weighting choices.")

    sp = spearman.copy()
    sp.index   = [scenario_labels.get(i, i).split("—")[-1].strip() for i in sp.index]
    sp.columns = sp.index

    fig_sp = px.imshow(
        sp.astype(float),
        color_continuous_scale="Blues",
        zmin=0.8, zmax=1.0,
        text_auto=".3f",
        aspect="auto",
    )
    fig_sp.update_layout(height=350, margin=dict(l=60, r=20, t=20, b=40))
    st.plotly_chart(fig_sp, use_container_width=True)

    st.subheader("Max Rank Displacement Per Country")
    st.caption("How many rank positions a country's rank shifts across the four weighting scenarios.")

    shift_disp = shifts[["Country", "max_shift"]].sort_values("max_shift", ascending=False).head(30)
    fig_shift = px.bar(
        shift_disp, x="max_shift", y="Country", orientation="h",
        color="max_shift", color_continuous_scale="Reds",
        labels={"max_shift": "Max Rank Shift"},
    )
    fig_shift.update_layout(
        height=550, yaxis={"categoryorder": "total ascending"},
        margin=dict(l=0, r=20, t=10, b=0), coloraxis_showscale=False,
    )
    st.plotly_chart(fig_shift, use_container_width=True)

    st.subheader("All Scenario Scores")
    st.dataframe(scenarios, use_container_width=True, hide_index=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 6 — DIAGNOSTICS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_diag:
    st.subheader("Distribution Diagnostics Per Pillar")
    st.dataframe(
        diag.style.background_gradient(subset=["skew", "kurtosis"], cmap="coolwarm")
             .format({c: "{:.4f}" for c in diag.select_dtypes("float").columns}),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Raw Pillar Distributions (Box Plots)")
    raw_melted = raw.melt(id_vars=["Country", "ISO3", "Region"],
                          value_vars=PILLAR_COLS, var_name="Pillar", value_name="Prevalence (%)")
    fig_box = px.box(
        raw_melted, x="Pillar", y="Prevalence (%)",
        color="Pillar", points="all",
        hover_data=["Country", "Region"],
    )
    fig_box.update_layout(height=450, showlegend=False, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig_box, use_container_width=True)

    st.subheader("Raw Data Table")
    st.dataframe(raw, use_container_width=True, hide_index=True)
