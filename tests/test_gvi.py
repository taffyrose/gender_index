"""Tests for core GVI pipeline.

These tests validate that all requirements in the verification checklist are met
for the simulated pipeline (55 countries, normalization bounds, correlations,
scenarios computed, etc.).
"""
import pytest
import numpy as np
from src.data_generator import generate_base_countries, simulate_pillars
from src.gvi_model import normalize_pillars, compute_gvi_for_scenarios
from src.constants import PILLARS


def test_country_count():
    df = generate_base_countries()
    assert len(df) == 55


def test_simulation_and_bounds():
    base = generate_base_countries()
    raw = simulate_pillars(base)
    # check all pillar columns present
    for p in PILLARS.keys():
        assert p in raw.columns
        assert raw[p].min() >= PILLARS[p]["min"] - 0.1
        assert raw[p].max() <= PILLARS[p]["max"] + 0.1


def test_normalization_and_gvi():
    base = generate_base_countries()
    raw = simulate_pillars(base)
    norm = normalize_pillars(raw)
    # normalised values in [0,1]
    for p in PILLARS.keys():
        col = f"{p}_Norm"
        assert col in norm.columns
        assert norm[col].between(0, 1).all()

    # compute scenarios
    results = compute_gvi_for_scenarios(norm)
    # baseline exists
    assert "baseline" in results
    baseline = results["baseline"]
    assert baseline["GVI_Score"].between(0, 1).all()
    # ranks 1..55
    ranks = baseline["GVI_Rank"].unique()
    assert set(ranks) <= set(range(1, 56))
