"""Simulate pillar data using truncated normals and induced correlations.

This module implements the truncated normal draws per pillar, applies
regional offsets, and induces cross-pillar correlations using a linear
mixing method: Y = rho * X_std + sqrt(1-rho^2) * Z, then rescales to the
original distribution range. Seed is fixed for reproducibility.
"""
from typing import Dict
import numpy as np
import pandas as pd
from scipy.stats import truncnorm
from src.constants import COUNTRIES, PILLARS, REGIONAL_OFFSETS


RNG_SEED = 2024


def _truncnorm_draw(mean: float, sd: float, low: float, high: float, size: int, rng: np.random.Generator) -> np.ndarray:
    """Draw samples from a truncated normal distribution.

    Args:
        mean: distribution mean
        sd: distribution standard deviation
        low: lower bound
        high: upper bound
        size: number of draws
        rng: numpy random Generator

    Returns:
        Array of draws
    """
    a, b = (low - mean) / sd, (high - mean) / sd
    # scipy truncnorm.rvs uses global seed via random_state; we draw via standard normal then clip
    samples = truncnorm.rvs(a, b, loc=mean, scale=sd, size=size, random_state=rng)
    return samples


def generate_base_countries() -> pd.DataFrame:
    """Return a DataFrame of the 55 AU member states with Region and ISO3.

    Returns:
        DataFrame with columns: Country, ISO3, Region
    """
    df = pd.DataFrame(COUNTRIES)
    assert len(df) == 55, "Must have all 55 AU states"
    return df


def simulate_pillars(countries_df: pd.DataFrame) -> pd.DataFrame:
    """Simulate raw pillar prevalence (%) for each country.

    Steps:
    - For each pillar, draw truncated normal samples around pillar mean
      plus region-specific offset.
    - Induce correlations: Physical <-> Psychological (rho~0.6), Emotional <-> Psychological (rho~0.5).
    - Round to 1 decimal place.

    Args:
        countries_df: base countries DataFrame

    Returns:
        DataFrame with raw pillar columns added.
    """
    rng = np.random.default_rng(RNG_SEED)
    df = countries_df.copy()
    n = len(df)

    # initial independent draws
    draws: Dict[str, np.ndarray] = {}
    for pillar, spec in PILLARS.items():
        # apply regional offsets per-country
        means = []
        for _, row in df.iterrows():
            region = row["Region"]
            offset = REGIONAL_OFFSETS.get(region, {}).get(pillar, 0.0)
            means.append(spec["mean"] + offset)
        means = np.array(means)
        samples = np.empty(n)
        # draw per-country using per-country mean
        for i in range(n):
            samples[i] = _truncnorm_draw(means[i], spec["std"], spec["min"], spec["max"], 1, rng)[0]
        draws[pillar] = samples

    # Induce correlations using linear mixing
    # Physical <- correlated with Psychological (rho=0.6)
    # Emotional <- correlated with Psychological (rho=0.5)
    psych = draws["Psychological"]
    # standardize psych
    psych_std = (psych - psych.mean()) / psych.std(ddof=0)

    def mix_with(psych_std_arr, target_raw, rho):
        # create independent Z
        z = rng.standard_normal(len(target_raw))
        mixed_std = rho * psych_std_arr + np.sqrt(1 - rho ** 2) * ((z - z.mean()) / z.std(ddof=0))
        # rescale mixed_std to match original target raw distribution mean/std
        tgt_mean = np.mean(target_raw)
        tgt_std = np.std(target_raw, ddof=0)
        rescaled = mixed_std * tgt_std + tgt_mean
        # clip to pillar bounds
        return rescaled

    # mix Physical
    phys_mixed = mix_with(psych_std, draws["Physical"], rho=0.6)
    draws["Physical"] = np.clip(phys_mixed, PILLARS["Physical"]["min"], PILLARS["Physical"]["max"])

    # mix Emotional
    emot_mixed = mix_with(psych_std, draws["Emotional"], rho=0.5)
    draws["Emotional"] = np.clip(emot_mixed, PILLARS["Emotional"]["min"], PILLARS["Emotional"]["max"])

    # assemble into df
    for pillar in PILLARS.keys():
        df[pillar] = np.round(draws[pillar], 1)

    return df
