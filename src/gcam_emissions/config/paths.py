"""Filesystem layout for gcam-emissions.

Two roots matter here. Reference tables ship *inside* the package so that a
consumer only has to install it, while every generated artifact lands under a
workspace root the caller controls. Set ``GCAM_EMISSIONS_HOME`` to point the
outputs somewhere other than the current working directory.
"""

from __future__ import annotations

import os
from pathlib import Path

# Packaged, read-only reference tables (sector inventory, crosswalks, EF catalog).
PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_DIR = PACKAGE_ROOT / "reference"

# Backwards-compatible alias for the ported modules.
NONPOWER_REFERENCE_DIR = REFERENCE_DIR


def _workspace_root() -> Path:
    configured = os.environ.get("GCAM_EMISSIONS_HOME")
    return Path(configured).expanduser().resolve() if configured else Path.cwd().resolve()


WORKSPACE_ROOT = _workspace_root()
PROJECT_ROOT = WORKSPACE_ROOT

DATA_DIR = WORKSPACE_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"
RESULTS_DIR = WORKSPACE_ROOT / "results"
RESULTS_DIAGNOSTICS_DIR = RESULTS_DIR / "diagnostics"
MODEL_INPUTS_DIR = WORKSPACE_ROOT / "model_inputs"

# Non-power inventory and emission-factor products.
NONPOWER_PROCESSED_DIR = PROCESSED_DIR / "nonpower_emissions"
NONPOWER_INTERIM_DIR = INTERIM_DIR / "nonpower_emissions"
NONPOWER_DIAGNOSTIC_DIR = RESULTS_DIAGNOSTICS_DIR / "nonpower_emissions"

# GCAM scenario handoffs and the APHIAM-ready interface written from them.
GCAM_INPUTS_DIR = MODEL_INPUTS_DIR / "gcam"
GCAM_NZK_ARCHIVE = GCAM_INPUTS_DIR / "CORE_9_NZ_2026-8-7T12_32_50+09_00.xml.zip"
GCAM_NZK_APHIAM_DIR = MODEL_INPUTS_DIR / "interface" / "gcam_kaist" / "nzk"

# Korean inputs consumed by the spatial allocator.
CAPSS_RAW_DIR = RAW_DIR / "capss"
CAPSS_INTERIM_DIR = INTERIM_DIR / "capss"
AIRKOREA_RAW_DIR = RAW_DIR / "airkorea"
AIRKOREA_STATION_RAW_DIR = AIRKOREA_RAW_DIR / "stations"
