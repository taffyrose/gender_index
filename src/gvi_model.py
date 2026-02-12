"""Normalization and aggregation functions for the GVI.

Implements exogenous min-max normalization (OECD §4) and weighted geometric
mean aggregation (OECD §5) with epsilon safeguard to avoid zero-collapse.
"""
from typing import Dict, Tuple
import numpy as np
import pandas as pd
from scipy.stats import zscore
from src.constants import PILLARS, THEORETICAL_MIN, THEORETICAL_MAX, WEIGHTING_SCENARIOS, EPSILON


def normalize_pillars(df: pd.DataFrame) -> pd.DataFrame:
    """Apply exogenous min-max normalization to pillar columns.

    Normalized_Value = (X - Theoretical_Min) / (Theoretical_Max - Theoretical_Min)

    Args:
        df: DataFrame with raw pillar percentage columns

    Returns:
        DataFrame with additional `{Pillar}_Norm` columns clamped to [0,1]
    """
    out = df.copy()
    for pillar in PILLARS.keys():
        col = pillar
        norm_col = f"{pillar}_Norm"
        out[norm_col] = (out[col] - THEORETICAL_MIN) / (THEORETICAL_MAX - THEORETICAL_MIN)
        out[norm_col] = out[norm_col].clip(0.0, 1.0)
    return out


def _weighted_geometric_mean(norm_values: np.ndarray, weights: np.ndarray, epsilon: float = EPSILON) -> float:
    """Compute weighted geometric mean with epsilon safeguard.

    We use (P_i + eps) to prevent the product from being zero if any P_i==0.
    Geometric mean penalises imbalance between dimensions, supporting
    non-substitutability.
    """
    assert norm_values.shape == weights.shape
    # ensure non-negative
    norm_values = np.maximum(norm_values, 0.0)
    return float(np.prod((norm_values + epsilon) ** weights))


def compute_gvi_for_scenarios(norm_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Compute GVI scores for all weighting scenarios.

    Returns a dict keyed by scenario name with DataFrames containing
    normalized pillars, GVI score and rank (1 = worst).
    """
    results = {}
    # gather normalized columns in fixed order
    pillar_order = list(PILLARS.keys())
    norm_cols = [f"{p}_Norm" for p in pillar_order]

    for scenario_name, weights_map in WEIGHTING_SCENARIOS.items():
        df = norm_df.copy()
        weights = np.array([weights_map[p] for p in pillar_order], dtype=float)
        # compute GVI per country
        gvi_scores = []
        for _, row in df.iterrows():
            vals = row[norm_cols].to_numpy(dtype=float)
            score = _weighted_geometric_mean(vals, weights)
            gvi_scores.append(score)
        df["GVI_Score"] = np.round(gvi_scores, 6)
        # rank 1 = worst (highest GVI)
        df["GVI_Rank"] = df["GVI_Score"].rank(method="min", ascending=False).astype(int)
        # sort by rank for convenience
        df = df.sort_values("GVI_Rank").reset_index(drop=True)
        results[scenario_name] = df
    return results
