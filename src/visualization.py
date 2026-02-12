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


def _load_africa_shapefile() -> gpd.GeoDataFrame:
    """Load Natural Earth countries and filter to Africa.

    Tries geodatasets (geopandas >= 0.14 recommended approach) first,
    then falls back to legacy gpd.datasets, then to a local file in data/.
    """
    world = None
    # Attempt 1: geodatasets package (geopandas >= 0.14 recommended)
    try:
        import geodatasets
        world = gpd.read_file(geodatasets.get_path("naturalearth.land"))
        # geodatasets naturalearth.land has no country boundaries; use lowres instead
        world = gpd.read_file(geodatasets.get_path("naturalearth lowres"))
    except Exception:
        world = None
    # Attempt 2: legacy geopandas datasets (geopandas < 0.14)
    if world is None:
        try:
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
        except Exception:
            world = None
    # Attempt 3: local shapefile
    if world is None:
        try:
            world = gpd.read_file("data/ne_110m_admin_0_countries.shp")
        except Exception as e:
            raise RuntimeError(
                "Could not load Natural Earth dataset. Install geodatasets (`pip install geodatasets`) "
                "or place shapefile in ./data/ne_110m_admin_0_countries.shp"
            ) from e

    # Attempt to harmonize ISO codes
    if "iso_a3" in world.columns:
        world = world.rename(columns={"iso_a3": "ISO3"})
    elif "ISO_A3" in world.columns:
        world = world.rename(columns={"ISO_A3": "ISO3"})

    # Filter Africa by continent if possible, else by bounding box (best-effort)
    if "continent" in world.columns:
        africa = world[world["continent"] == "Africa"].copy()
    else:
        # crude bbox filter: longitude between -25 and 60, latitude between -40 and 40
        africa = world.cx[-25:60, -40:40].copy()

    # Fix known ISO issues
    iso_fixes = {"SOM": "SOM", "SSD": "SSD", "ESH": "ESH"}
    # Ensure we have an ISO3 column
    if "ISO3" not in africa.columns:
        # try common alternatives
        if "adm0_a3" in africa.columns:
            africa = africa.rename(columns={"adm0_a3": "ISO3"})
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
    # Shapefile field names limited to 10 chars; create truncated copy
    shp_copy = merged.copy()
    # Truncate column names to 10 chars for shapefile compatibility
    shp_copy.columns = [c[:10] for c in shp_copy.columns]
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
