"""Sensitivity analysis and robustness diagnostics for the GVI.

Implements Spearman rank correlations across weighting scenarios,
distribution diagnostics (skewness, kurtosis, Shapiro-Wilk), z-score
outlier detection, and rank shift calculations per OECD Chapter 6.
"""
from typing import Dict, Tuple
import pandas as pd
import numpy as np
from scipy.stats import spearmanr, skew, kurtosis, shapiro, zscore
from src.constants import PILLARS, WEIGHTING_SCENARIOS


def run_sensitivity_and_diagnostics(all_results: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """Compute diagnostics and export CSVs under ./outputs/.

    Args:
        all_results: dict of scenario DataFrames (from compute_gvi_for_scenarios)

    Returns:
        dict of diagnostic DataFrames
    """
    outputs = {}

    # 01_raw_data.csv
    baseline = all_results["baseline"]
    raw_cols = list(PILLARS.keys())
    raw_df = baseline[["Country", "ISO3", "Region"] + raw_cols].copy()
    raw_df.to_csv("outputs/01_raw_data.csv", index=False)
    outputs["raw"] = raw_df

    # 03_pillar_breakdown.csv (normalized)
    norm_cols = [f"{p}_Norm" for p in PILLARS.keys()]
    pillar_break = baseline[["Country", "ISO3", "Region"] + norm_cols].copy()
    pillar_break.to_csv("outputs/03_pillar_breakdown.csv", index=False)
    outputs["pillar_breakdown"] = pillar_break

    # 04_sensitivity_scenarios.csv -> compile scores and ranks
    scen_frames = []
    for name, df in all_results.items():
        tmp = df[["Country", "ISO3", "GVI_Score", "GVI_Rank"]].copy()
        tmp = tmp.rename(columns={"GVI_Score": f"GVI_{name}_Score", "GVI_Rank": f"GVI_{name}_Rank"})
        scen_frames.append(tmp.set_index(["Country", "ISO3"]))
    scen_concat = pd.concat(scen_frames, axis=1).reset_index()
    scen_concat.to_csv("outputs/04_sensitivity_scenarios.csv", index=False)
    outputs["scenarios"] = scen_concat

    # 05_correlation_matrix.csv (Pearson across raw pillars)
    corr = baseline[raw_cols].corr(method="pearson")
    corr.to_csv("outputs/05_correlation_matrix.csv")
    outputs["correlation"] = corr

    # 06_distribution_diagnostics.csv
    dist_rows = []
    for p in raw_cols:
        arr = baseline[p].to_numpy()
        mean_ = float(np.mean(arr))
        std_ = float(np.std(arr, ddof=0))
        min_ = float(np.min(arr))
        max_ = float(np.max(arr))
        skew_ = float(skew(arr))
        kurt_ = float(kurtosis(arr))
        try:
            sw_stat, sw_p = shapiro(arr)
        except Exception:
            sw_stat, sw_p = (np.nan, np.nan)
        dist_rows.append({
            "Pillar": p,
            "mean": mean_,
            "std": std_,
            "min": min_,
            "max": max_,
            "skew": skew_,
            "kurtosis": kurt_,
            "shapiro_stat": sw_stat,
            "shapiro_p": sw_p,
        })
    dist_df = pd.DataFrame(dist_rows)
    dist_df.to_csv("outputs/06_distribution_diagnostics.csv", index=False)
    outputs["distribution"] = dist_df

    # 07_zscore_outliers.csv
    z_df = baseline.copy().reset_index(drop=True)
    zvals = zscore(z_df[raw_cols].to_numpy(), ddof=0)
    zmask = np.abs(zvals) > 2.5
    rows = []
    for i in range(len(z_df)):
        for j, p in enumerate(raw_cols):
            if zmask[i, j]:
                rows.append({"Country": z_df.at[i, "Country"], "ISO3": z_df.at[i, "ISO3"], "Pillar": p, "z": float(zvals[i, j])})
    outliers = pd.DataFrame(rows)
    outliers.to_csv("outputs/07_zscore_outliers.csv", index=False)
    outputs["outliers"] = outliers

    # 08_rank_stability_spearman.csv -> pairwise Spearman between scenarios
    scenario_names = list(all_results.keys())
    spearman_mat = pd.DataFrame(index=scenario_names, columns=scenario_names, dtype=float)
    for i, a in enumerate(scenario_names):
        for j, b in enumerate(scenario_names):
            if i <= j:
                rho, _ = spearmanr(all_results[a]["GVI_Rank"], all_results[b]["GVI_Rank"])
                spearman_mat.loc[a, b] = rho
                spearman_mat.loc[b, a] = rho
    spearman_mat.to_csv("outputs/08_rank_stability_spearman.csv")
    outputs["spearman"] = spearman_mat

    # 09_rank_shifts.csv -> max rank displacement per country across scenarios
    ranks = {name: df.set_index("Country")["GVI_Rank"] for name, df in all_results.items()}
    ranks_df = pd.concat(ranks, axis=1)
    # compute max displacement
    ranks_df["max_shift"] = ranks_df.max(axis=1) - ranks_df.min(axis=1)
    ranks_df_out = ranks_df.reset_index().rename(columns={0: "Country"})
    ranks_df_out.to_csv("outputs/09_rank_shifts.csv", index=False)
    outputs["rank_shifts"] = ranks_df_out

    # 02_gvi_ranked.csv -> baseline GVI with rank
    baseline[["Country", "ISO3", "Region", "GVI_Score", "GVI_Rank"]].to_csv("outputs/02_gvi_ranked.csv", index=False)

    # Print top/bottom 10
    worst10 = baseline.head(10)[["Country", "GVI_Score"]]
    best10 = baseline.tail(10)[["Country", "GVI_Score"]]
    print("Top 10 Worst (highest GVI):")
    print(worst10.to_string(index=False))
    print("\nTop 10 Best (lowest GVI):")
    print(best10.to_string(index=False))

    return outputs
