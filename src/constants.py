"""Constants and configuration for the GVI project.

This module holds the list of 55 AU member states, pillar definitions,
simulation parameters, regional offsets, and weighting scenarios.
All settings are declared centrally to make the pipeline reproducible
and auditable per OECD best practice.
"""
from typing import Dict, List, TypedDict


class PillarSpec(TypedDict):
    min: float
    max: float
    mean: float
    std: float


PROJECT_TITLE = "Africa Gender Violence Index (GVI)"

# The canonical list of 55 AU member states with ISO3 and region
# Regions: North, West, Central, East, Southern
COUNTRIES: List[Dict[str, str]] = [
    # North (7)
    {"Country": "Algeria", "ISO3": "DZA", "Region": "North"},
    {"Country": "Egypt", "ISO3": "EGY", "Region": "North"},
    {"Country": "Libya", "ISO3": "LBY", "Region": "North"},
    {"Country": "Mauritania", "ISO3": "MRT", "Region": "North"},
    {"Country": "Morocco", "ISO3": "MAR", "Region": "North"},
    {"Country": "Tunisia", "ISO3": "TUN", "Region": "North"},
    {"Country": "Sahrawi Republic", "ISO3": "ESH", "Region": "North"},
    # West (15)
    {"Country": "Benin", "ISO3": "BEN", "Region": "West"},
    {"Country": "Burkina Faso", "ISO3": "BFA", "Region": "West"},
    {"Country": "Cabo Verde", "ISO3": "CPV", "Region": "West"},
    {"Country": "Côte d'Ivoire", "ISO3": "CIV", "Region": "West"},
    {"Country": "Gambia", "ISO3": "GMB", "Region": "West"},
    {"Country": "Ghana", "ISO3": "GHA", "Region": "West"},
    {"Country": "Guinea", "ISO3": "GIN", "Region": "West"},
    {"Country": "Guinea-Bissau", "ISO3": "GNB", "Region": "West"},
    {"Country": "Liberia", "ISO3": "LBR", "Region": "West"},
    {"Country": "Mali", "ISO3": "MLI", "Region": "West"},
    {"Country": "Niger", "ISO3": "NER", "Region": "West"},
    {"Country": "Nigeria", "ISO3": "NGA", "Region": "West"},
    {"Country": "Senegal", "ISO3": "SEN", "Region": "West"},
    {"Country": "Sierra Leone", "ISO3": "SLE", "Region": "West"},
    {"Country": "Togo", "ISO3": "TGO", "Region": "West"},
    # Central (8)
    {"Country": "Cameroon", "ISO3": "CMR", "Region": "Central"},
    {"Country": "Central African Republic", "ISO3": "CAF", "Region": "Central"},
    {"Country": "Chad", "ISO3": "TCD", "Region": "Central"},
    {"Country": "Congo", "ISO3": "COG", "Region": "Central"},
    {"Country": "DR Congo", "ISO3": "COD", "Region": "Central"},
    {"Country": "Equatorial Guinea", "ISO3": "GNQ", "Region": "Central"},
    {"Country": "Gabon", "ISO3": "GAB", "Region": "Central"},
    {"Country": "São Tomé and Príncipe", "ISO3": "STP", "Region": "Central"},
    # East (15)
    {"Country": "Burundi", "ISO3": "BDI", "Region": "East"},
    {"Country": "Comoros", "ISO3": "COM", "Region": "East"},
    {"Country": "Djibouti", "ISO3": "DJI", "Region": "East"},
    {"Country": "Eritrea", "ISO3": "ERI", "Region": "East"},
    {"Country": "Ethiopia", "ISO3": "ETH", "Region": "East"},
    {"Country": "Kenya", "ISO3": "KEN", "Region": "East"},
    {"Country": "Madagascar", "ISO3": "MDG", "Region": "East"},
    {"Country": "Mauritius", "ISO3": "MUS", "Region": "East"},
    {"Country": "Rwanda", "ISO3": "RWA", "Region": "East"},
    {"Country": "Seychelles", "ISO3": "SYC", "Region": "East"},
    {"Country": "Somalia", "ISO3": "SOM", "Region": "East"},
    {"Country": "South Sudan", "ISO3": "SSD", "Region": "East"},
    {"Country": "Sudan", "ISO3": "SDN", "Region": "East"},
    {"Country": "Tanzania", "ISO3": "TZA", "Region": "East"},
    {"Country": "Uganda", "ISO3": "UGA", "Region": "East"},
    # Southern (10)
    {"Country": "Angola", "ISO3": "AGO", "Region": "Southern"},
    {"Country": "Botswana", "ISO3": "BWA", "Region": "Southern"},
    {"Country": "Eswatini", "ISO3": "SWZ", "Region": "Southern"},
    {"Country": "Lesotho", "ISO3": "LSO", "Region": "Southern"},
    {"Country": "Malawi", "ISO3": "MWI", "Region": "Southern"},
    {"Country": "Mozambique", "ISO3": "MOZ", "Region": "Southern"},
    {"Country": "Namibia", "ISO3": "NAM", "Region": "Southern"},
    {"Country": "South Africa", "ISO3": "ZAF", "Region": "Southern"},
    {"Country": "Zambia", "ISO3": "ZMB", "Region": "Southern"},
    {"Country": "Zimbabwe", "ISO3": "ZWE", "Region": "Southern"},
]

assert len(COUNTRIES) == 55, "Must have all 55 AU states"

# Pillar specifications (ranges in % with simulation mean and std)
PILLARS: Dict[str, PillarSpec] = {
    "Sexual": {"min": 5.0, "max": 45.0, "mean": 22.0, "std": 10.0},
    "Physical": {"min": 10.0, "max": 55.0, "mean": 30.0, "std": 12.0},
    "Psychological": {"min": 15.0, "max": 65.0, "mean": 38.0, "std": 13.0},
    "Economic": {"min": 5.0, "max": 40.0, "mean": 20.0, "std": 9.0},
    "Environmental": {"min": 5.0, "max": 35.0, "mean": 18.0, "std": 8.0},
    "Emotional": {"min": 10.0, "max": 55.0, "mean": 32.0, "std": 11.0},
}

# Theoretical normalization bounds (exogenous)
THEORETICAL_MIN = 0.0
THEORETICAL_MAX = 70.0

# Regional clustering offsets (example offsets to create heterogeneity)
# Offsets added to pillar means by region (North, West, Central, East, Southern)
REGIONAL_OFFSETS: Dict[str, Dict[str, float]] = {
    "North": {
        "Sexual": -3.0,
        "Physical": -2.0,
        "Psychological": -1.0,
        "Economic": -2.0,
        "Environmental": -1.5,
        "Emotional": -1.0,
    },
    "West": {
        "Sexual": 1.0,
        "Physical": 2.0,
        "Psychological": 2.0,
        "Economic": 1.0,
        "Environmental": 0.5,
        "Emotional": 1.5,
    },
    "Central": {
        "Sexual": 4.0,
        "Physical": 3.0,
        "Psychological": 3.5,
        "Economic": 2.0,
        "Environmental": 2.5,
        "Emotional": 2.0,
    },
    "East": {
        "Sexual": 2.0,
        "Physical": 1.5,
        "Psychological": 1.0,
        "Economic": 0.5,
        "Environmental": 1.0,
        "Emotional": 1.0,
    },
    "Southern": {
        "Sexual": 0.5,
        "Physical": 0.0,
        "Psychological": 0.5,
        "Economic": -0.5,
        "Environmental": -1.0,
        "Emotional": 0.0,
    },
}

# Weighting scenarios
WEIGHTING_SCENARIOS = {
    "baseline": {"Sexual": 1/6, "Physical": 1/6, "Psychological": 1/6, "Economic": 1/6, "Environmental": 1/6, "Emotional": 1/6},
    "A_psych_focus": {"Sexual": 0.10, "Physical": 0.10, "Psychological": 0.40, "Economic": 0.10, "Environmental": 0.15, "Emotional": 0.15},
    "B_econ_focus": {"Sexual": 0.10, "Physical": 0.10, "Psychological": 0.10, "Economic": 0.40, "Environmental": 0.15, "Emotional": 0.15},
    "C_phys_focus": {"Sexual": 0.15, "Physical": 0.40, "Psychological": 0.10, "Economic": 0.10, "Environmental": 0.10, "Emotional": 0.15},
}

# Epsilon for geometric mean to avoid zero-collapse
EPSILON = 1e-6
