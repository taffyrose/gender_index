"""Entry point for the Africa Gender Violence Index (GVI) pipeline.

This script runs the full pipeline: data generation, normalization,
aggregation using a weighted geometric mean, sensitivity analysis,
diagnostics, and visualization/exports.
"""
from src.constants import PROJECT_TITLE
from src.data_generator import generate_base_countries, simulate_pillars
from src.gvi_model import normalize_pillars, compute_gvi_for_scenarios
from src.sensitivity import run_sensitivity_and_diagnostics
from src.visualization import produce_maps_and_exports
import os


def main() -> None:
    """Run the full GVI pipeline and export outputs.

    Orchestrates data generation, scoring, sensitivity analysis, export of CSVs, and map generation.
    """
    # Ensure output directories exist
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("shapefiles", exist_ok=True)

    # Step 1: countries
    countries_df = generate_base_countries()

    # Step 2: simulate raw pillar data
    raw_df = simulate_pillars(countries_df)

    # Step 3: normalize
    norm_df = normalize_pillars(raw_df)

    # Step 4-5: compute GVI for scenarios and diagnostics
    all_results = compute_gvi_for_scenarios(norm_df)

    # Step 6-8: sensitivity, diagnostics, exports
    diagnostics = run_sensitivity_and_diagnostics(all_results)

    # Step 7: visualizations and geospatial exports
    produce_maps_and_exports(all_results["baseline"], norm_df)

    print("GVI pipeline completed. Outputs in ./outputs and ./shapefiles/")


if __name__ == "__main__":
    print(f"Running: {PROJECT_TITLE}")
    main()
