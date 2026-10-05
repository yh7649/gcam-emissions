# Korean power-sector emission-factor evidence

This directory preserves the literature evidence and review structure migrated
from NZK-APHIAM. In this repository it supports factor research and validation;
it is not an automatically approved factor table.

## Contents

- `literature_catalog.csv`: source-level scope and evidence classification.
- `literature_benchmarks.csv`: transcribed numeric evidence in long form.
- `literature_plant_crosswalk.csv`: reviewed project-to-literature plant and
  unit boundaries; no fuzzy boundary matching is permitted.
- `literature_comparison_rules.csv`: allowed comparisons and explicit
  noncomparability reasons.
- `literature_pdf_inventory.csv`: local filenames, citations, and SHA-256
  checksums.
- `korea_ef_references/`: the source PDFs and their source manifest.

The CAPSS Handbook VII PDF in the nested directory is also the default input to
`gcam_emissions.factors.capss_handbook`.

## Evidence and comparison classes

The archive distinguishes what a source reports from whether it can be compared
to a project factor. Evidence types include direct or derivable output factors,
input-based factors, supporting measurements, and secondary reports.

Comparison classes retained from the NZK-APHIAM validation work are:

- `A_exact_reproduction`: same plant, units, year, pollutant, reporting
  boundary, denominator, and temporal coverage;
- `B_plant_pipeline_validation`: same plant/unit boundary and year, with an
  external emissions or generation pipeline;
- `C_aggregate_consistency_check`: compatible year/fuel fleet aggregation;
- `D_contextual_benchmark`: relevant context without a direct match; and
- `X_not_comparable`: incompatible units, normalization, pollutant, or scope.

Only classes A and B qualify as plant-level external validation. Class C is an
aggregate check. Classes D and X do not receive an ordinary percent error.
Sparse direct Korean literature is retained as a real coverage result rather
than weakened matching criteria.

## Source-specific cautions

- Lee et al. (2025) reports 2022 coal-complex generation and NOx, SOx, and TSP
  mass from CleanSYS/EPSIS, enabling derivable output factors at its stated
  plant boundaries.
- KEEI (2017) reports a combined-pollutant result for exact 2016 plant/unit
  groups; it must not be split into invented pollutant values.
- MOTIE (2019) provides 2017 national coal/LNG fleet averages and is an
  aggregate consistency source.
- Seo, Kim, and Jeon (2019) provides an output-factor method and anonymous oil
  units; it is contextual unless the exact units and years are resolved.
- CAPSS Handbook VII and Yu et al. (2021) are fuel-input-normalized sources;
  they are not direct `kg/MWh` comparisons.
- The Solutions for Our Climate biomass report is secondary evidence.

Missing emissions are not zero. Annual output factors, when derived from
monthly data, use ratio-of-sums rather than an arithmetic mean of monthly
ratios.

