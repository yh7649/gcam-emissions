# Korea emission-factor collection

## Scope and status

This repository is now the system of record for the emission-factor work that
started in NZK-APHIAM. The migration preserves the source evidence, extraction
targets, factor candidates, mapping rules, and explicit gaps while keeping the
downstream health-model repository focused on consuming emitted mass.

There are two complementary collections:

- the packaged non-power catalog under `src/gcam_emissions/reference/`; and
- the Korean power-sector literature archive under
  `docs/references/emission_factor_validation/`.

The normalized 912-row imported catalog is not yet an approved production
database: every imported or automatically extracted factor remains
`production_ready=false`. The separately reviewed 135-row target records exact
assignments, conditional factor sets/formulas, explicit gaps, and direct-
emissions boundary decisions without automatically promoting the underlying
bulk catalog.

The current 135-row GCAM-KAIST research target is
`docs/gcam_kaist_ef_target_table.csv`. It reconciles the lab's vetted
GCAM-USA/NEI sector list to GCAM-KAIST's native taxonomy. It is a working
research table, not a public runtime interface. `make fill-kaist-efs` now fills
all 135 fourth-column cells reproducibly: 4 exact factors, 75 conditional
factor sets or formulas, 35 not-applicable boundary decisions, and 21 explicit
research gaps. The generated row audit independently records readiness, source
IDs, source locations, and the owner review record. A populated cell therefore
does not imply that its denominator is ready to multiply by GCAM activity.

## What was carried over from NZK-APHIAM

The non-power collection was migrated without changing its evidence:

- 89 inventory activities;
- 181 GCAM/CAPSS crosswalk rows;
- 608 pollutant-specific legal denominator rows;
- 912 imported factor candidates, including 887 Handbook VI rows awaiting a
  row-level comparison to Handbook VII;
- 2,067 candidate inventory links across 41 activities;
- six non-mass-normalized evidence records; and
- 11 explicit collection gaps.

The verified Handbook VII extraction work is also preserved. Its target
registry covers 327 unique PDF pages and 86 direct-emission activities. The
existing extractor identified 123 factor/speciation tables, reconstructed 129
table occurrences, and emitted 3,250 standard-column candidates. Those
generated products stay under `data/interim/` and are not tracked.

All 14 migrated non-power CSVs are packaged under
`src/gcam_emissions/reference/`; see [reference_tables.md](reference_tables.md)
for file-by-file semantics. The historical NZK-APHIAM copies are not duplicated
under `docs/`.

The power evidence archive carries seven reviewed PDFs plus their catalog,
checksums, transcribed benchmarks, comparison rules, and plant crosswalk. This
includes Korean output-based, input-based, field-measurement, and contextual
sources. See the archive [README](references/emission_factor_validation/README.md)
for the comparability rules.

## Collection model

Keep these records separate throughout research and implementation:

```text
GCAM path + physical activity denominator
    -> factor evidence + inventory category + factor denominator
        -> annual effective factor after technology/control weights
            -> activity x factor = pollutant mass
                -> spatial surrogate or point source
```

A source is not usable merely because its sector label looks similar. A factor
record needs, at minimum:

- a stable evidence/source ID and a primary source location;
- pollutant and mass boundary;
- numeric value, formula, or range exactly as published;
- physical denominator and unit;
- fuel, technology, process, and control applicability;
- source year, measurement period, and geography;
- the GCAM activity and CAPSS category mapping decision; and
- review status, reviewer record, and unresolved assumptions.

Raw factors and annual effective factors are distinct. Fleet, model-year,
speed, route, fuel, process, and pollution-control shares belong in explicit
annual weighting inputs, not inside a manually entered raw factor.

CAPSS VII supplies BC either as an explicit Korean combustion factor or as a
source/fuel-specific fraction of PM2.5; the target retains that calculation
where the mapping is exact enough. CAPSS does not publish a parallel OC factor
system, so OC is not inferred from BC or PM2.5. That remains a separate
speciation-data gap rather than a zero.

Purchased electricity has no direct on-site factor. Electricity-only rows use
`direct_emissions_scope=none_on_site`; upstream emissions are assigned to the
power sector. Conversely, GCAM-KAIST `elec_*` sectors are in scope as the
interim forward-looking power source until NZK-APHIAM's MACRO projection is
ready.

## Source hierarchy

Use sources in this order:

1. official Korean methods and data, especially CAPSS/NIER and relevant
   ministries or official statistical systems;
2. Korean measured-emissions literature with documented technologies,
   controls, periods, sample sizes, and physical denominators; and
3. international factors only where Korean evidence is unavailable, with an
   explicit proxy rationale and uncertainty flag.

Provider access is recorded independently of source quality. A public program
announcement does not mean its row-level factor data are public.

## Reproducing and validating the collection

Set the workspace root before generating artifacts, then run:

```bash
export GCAM_EMISSIONS_HOME=/path/to/workspace
make validate
make inventory
make factors
make scrape-capss
make fill-kaist-efs
```

`make scrape-capss-verified` additionally downloads the official attachment in
memory and requires it to match the preserved PDF's SHA-256. It never
overwrites the preserved source.

The CAPSS VII manual used by the extractor is:

```text
docs/references/emission_factor_validation/
  korea_ef_references/CAPSS_Manual_VII_2025.pdf
```

Generated canonical tables go under `data/processed/nonpower_emissions/`;
extraction products go under `data/interim/nonpower_emissions/`; and validation
reports go under `results/diagnostics/nonpower_emissions/`. These are generated
artifacts and remain untracked.

## Immediate research queue

1. Resolve the target's 21 explicit Korea-specific research gaps and the
   technology/fuel/denominator weights blocking 75 conditional assignments.
2. Populate the target's CAPSS-equivalent-sector and CAPSS-emission-value
   fields without collapsing activity, factor, and spatial mappings.
3. Create a power-sector priority/inventory table parallel to, but separate
   from, the non-power inventory.
4. Parse formula-heavy road, aviation-ground-equipment, and other nonstandard
   Handbook VII tables.
5. Perform row-level Handbook VI-to-VII comparisons and human review; only a
   review record may promote a row to `production_ready=true`.
6. Add annual technology, fleet, route, and control weights and build reviewed
   spatial surrogates.
7. Incorporate the GCAM-global/CEDS mapping when the lab provides it.
