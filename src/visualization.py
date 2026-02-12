"""Visualization and geospatial exports for GVI.

Creates choropleth maps for the overall GVI and each pillar, exports
high-resolution PNGs, and writes ESRI Shapefile and GeoPackage outputs.
The module attempts to use Natural Earth data available via geopandas;
if unavailable, it expects a local file in `data/`.
"""
from typing import Tuple
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from src.constants import PILLARS


def _download_naturalearth_countries() -> gpd.GeoDataFrame:
    """Download and cache the Natural Earth 110m countries GeoJSON via pooch."""
    import pooch
    import zipfile
    import os
    import tempfile

    url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
    cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "gvi_naturalearth")
    os.makedirs(cache_dir, exist_ok=True)
    shp_path = os.path.join(cache_dir, "ne_110m_admin_0_countries.shp")

    if not os.path.exists(shp_path):
        zip_path = pooch.retrieve(
            url=url,
            known_hash=None,
            path=cache_dir,
            fname="ne_110m_admin_0_countries.zip",
        )
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(cache_dir)

    return gpd.read_file(shp_path)


def _load_africa_shapefile() -> gpd.GeoDataFrame:
    """Load Natural Earth countries and filter to Africa.

    Downloads and caches the Natural Earth 110m countries shapefile via pooch
    (geopandas >= 1.0 no longer bundles dataset files).
    Falls back to a local file in data/ if download fails.
    """
    world = None
    # Attempt 1: download / use cached Natural Earth countries (geopandas >= 1.0)
    try:
        world = _download_naturalearth_countries()
    except Exception:
        world = None
    # Attempt 2: local shapefile placed in data/
    if world is None:
        try:
            world = gpd.read_file("data/ne_110m_admin_0_countries.shp")
        except Exception as e:
            raise RuntimeError(
                "Could not load Natural Earth countries dataset. "
                "Ensure internet access for automatic download, or place "
                "ne_110m_admin_0_countries.shp in ./data/"
            ) from e

    # Harmonize ISO3 column — Natural Earth uses various column names
    cols_lower = {c.lower(): c for c in world.columns}
    if "ISO3" not in world.columns:
        for candidate in ("iso_a3", "ISO_A3", "adm0_a3", "ADM0_A3", "iso3", "ISO3_EH"):
            if candidate in world.columns:
                world = world.rename(columns={candidate: "ISO3"})
                break
            if candidate.lower() in cols_lower:
                world = world.rename(columns={cols_lower[candidate.lower()]: "ISO3"})
                break

    # Some Natural Earth entries have ISO_A3 == "-99" for disputed territories;
    # fall back to ADM0_A3 for those rows
    if "ADM0_A3" in world.columns:
        mask = world["ISO3"] == "-99"
        world.loc[mask, "ISO3"] = world.loc[mask, "ADM0_A3"]

    # Filter Africa by continent column if available, else bounding box
    if "continent" in world.columns:
        africa = world[world["continent"] == "Africa"].copy()
    elif "CONTINENT" in world.columns:
        africa = world[world["CONTINENT"] == "Africa"].copy()
    else:
        africa = world.cx[-25:60, -40:40].copy()

    # Drop duplicates by ISO3
    africa = africa.drop_duplicates(subset=["ISO3"]).reset_index(drop=True)
    return africa


def produce_maps_and_exports(baseline_df: pd.DataFrame, norm_df: pd.DataFrame) -> None:
    """Join data to Africa shapefile and produce maps and shapefile/gpkg exports.

    Args:
        baseline_df: DataFrame from baseline scenario including `ISO3` and `GVI_Score`
        norm_df: DataFrame including normalized pillar columns for joins
    """
    africa = _load_africa_shapefile()

    # Join baseline scores
    merged = africa.merge(baseline_df, left_on="ISO3", right_on="ISO3", how="left")

    # Export combined GeoPackage and Shapefile
    # Shapefile field names limited to 10 chars; create truncated copy with dedup
    shp_copy = merged.copy()
    seen: dict = {}
    new_cols = []
    for c in shp_copy.columns:
        trunc = c[:10]
        if trunc in seen:
            seen[trunc] += 1
            trunc = trunc[:8] + str(seen[trunc])
        else:
            seen[trunc] = 0
        new_cols.append(trunc)
    shp_copy.columns = new_cols
    shp_copy.to_file("shapefiles/africa_gvi.shp")
    merged.to_file("shapefiles/africa_gvi.gpkg", layer="africa_gvi", driver="GPKG")

    # Overall GVI choropleth
    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    merged.plot(column="GVI_Score", cmap="YlOrRd", vmin=0, vmax=1, legend=True, ax=ax, missing_kwds={"color": "lightgrey"})
    ax.set_axis_off()
    ax.set_title("GVI Score (0=Best, 1=Worst)")
    plt.annotate("Ngorima & Moyo, 2024 | Simulated Data", xy=(0.1, 0.02), xycoords="figure fraction", fontsize=8)
    plt.tight_layout()
    plt.savefig("outputs/gvi_overall.png", dpi=300)
    plt.close(fig)

    # Individual pillar maps
    for pillar in PILLARS.keys():
        norm_col = f"{pillar}_Norm"
        fig, ax = plt.subplots(1, 1, figsize=(8, 8))
        merged.plot(column=norm_col, cmap="YlOrRd", vmin=0, vmax=1, legend=True, ax=ax, missing_kwds={"color": "lightgrey"})
        ax.set_axis_off()
        ax.set_title(f"{pillar} (normalized)")
        plt.annotate("Ngorima & Moyo, 2024 | Simulated Data", xy=(0.1, 0.02), xycoords="figure fraction", fontsize=8)
        plt.tight_layout()
        plt.savefig(f"outputs/gvi_{pillar.lower()}_map.png", dpi=300)
        plt.close(fig)

    # Ranking bar chart: top 15 worst + top 15 best
    ranked = baseline_df.sort_values("GVI_Score", ascending=False)
    top15 = ranked.head(15)
    bot15 = ranked.tail(15)[::-1]
    combined = pd.concat([top15, bot15])
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    ax.barh(combined["Country"], combined["GVI_Score"], color="firebrick")
    ax.invert_yaxis()
    ax.set_xlabel("GVI Score")
    ax.set_title("Top 15 Worst and Top 15 Best Countries by GVI")
    plt.tight_layout()
    plt.savefig("outputs/gvi_rank_barchart.png", dpi=300)
    plt.close(fig)
