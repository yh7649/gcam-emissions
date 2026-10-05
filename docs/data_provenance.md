# Emission-factor data provenance

The repository's MIT license applies to project code and documentation, not to
third-party publications or source data. The PDFs under
`docs/references/emission_factor_validation/korea_ef_references/` are retained
as research source material with bibliographic and download provenance in
`sources.csv` and checksums in `literature_pdf_inventory.csv`. Users must
follow the original publishers' terms when redistributing them.

## CAPSS handbook

The official 2025 *National Air Pollutant Emissions Estimation Method Handbook
VII* is the primary current methodology source. The preserved 412-page PDF has
SHA-256:

```text
fd84b21d6b0e54408e376ca027948a0355c65546d50a15b46ee0da1e08b7ed37
```

`make scrape-capss-verified` retrieves the official attachment in memory and
fails unless its checksum matches the preserved file. It does not update the
source silently. Extraction outputs retain PDF page, table, source-label, unit,
and normalization provenance.

## Imported non-power collection

The first-pass collection contributes 912 mass-normalized candidate factors,
six records that cannot be expressed as mass-normalized factors, and 11
explicit gaps. Of the factor candidates, 887 were transcribed from Handbook VI
through a secondary mirror. They are labeled
`superseded_pending_capss_vii_diff` and cannot be production-enabled before a
row-level comparison against the official Handbook VII source. The other 25
rows are Korean measurement-study candidates. All remain
`production_ready=false`.

The source workbook, derived coverage CSV, notebook-dependent builder, and
duplicate environment files were superseded during the original NZK-APHIAM
integration. Their useful normalized records, mapping rules, source registry,
validation behavior, and extraction targets are retained here. Generated
workbooks and diagnostics are reproducible views and are not tracked.

## Power-sector literature

The migrated archive contains output-normalized studies and reports, official
input-based factors, and field measurements. The benchmark type is always
retained: `direct_output_ef`, `derivable_output_ef`, `input_based_ef`,
`supporting_measurement`, or `secondary_report`.

Input-based factors are not converted to `kg/MWh` without separately sourced
heating value, heat rate, fuel composition, and control-efficiency assumptions.
PM2.5 is not treated as TSP. Plant-level percent comparisons require a reviewed
match on plant/unit boundary, year, fuel, technology, pollutant, mass boundary,
generation denominator, and temporal coverage.

## Generated data

Reference CSVs and source documents are tracked inputs. Code must not write to
`src/gcam_emissions/reference/` or overwrite the PDFs. Generated extraction,
catalog, diagnostic, emission, and spatial products belong under the workspace
root selected with `GCAM_EMISSIONS_HOME`, specifically `data/`, `results/`, or
`model_inputs/`.

