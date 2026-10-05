# gcam-emissions

Turns GCAM scenario output into speciated, spatially allocated air-pollutant
emissions that an atmospheric model can consume.

The pipeline is four stages, deliberately kept separate:

```text
GCAM scenario XML
  └─ activity      which GCAM path and unit gives the physical denominator
       └─ factor   which inventory category supplies the emission factor
            └─ mass     activity × factor × annual weights
                 └─ space    where that mass lands on the grid
```

Keeping the activity, factor, and spatial legs in separate tables is the point.
A single "GCAM sector → inventory sector" column has to serve three incompatible
purposes at once, and collapses them: a spatial-surrogate label such as
`onroad_gas` says *spread this over the road network*, not *this fuel is
gasoline*. Here those live in different files with different keys, so the
conflation is structurally impossible.

## Status

Extracted from [NZK-APHIAM](../NZK-APHIAM) so the mapping work can evolve on its
own. Korea (GCAM-KAIST activity, CAPSS factors) is the only wired region today.

Nothing in the packaged factor catalog is approved for analytical use: every row
carries `production_ready=false`. The pipeline runs end to end and its outputs
are screening diagnostics, not estimates. See
[`docs/reference_tables.md`](docs/reference_tables.md) for what each table means
and [`docs/roadmap.md`](docs/roadmap.md) for what is missing. The migrated
research history, collection rules, and Korean source archive are documented in
[`docs/emission_factor_collection.md`](docs/emission_factor_collection.md), with
licensing and chain-of-custody notes in
[`docs/data_provenance.md`](docs/data_provenance.md).

## Install

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

Reference tables ship inside the package, so a consumer only has to install it.
Generated artifacts go under a workspace root you control:

```bash
export GCAM_EMISSIONS_HOME=/path/to/workspace   # defaults to the current directory
```

## Layout

| Path | Role |
|---|---|
| `src/gcam_emissions/gcam/xml_extract.py` | stream a GCAM XML archive into an activity table |
| `src/gcam_emissions/native.py` | activity crosswalk, factor join, emissions projection |
| `src/gcam_emissions/inventory.py` | sector taxonomy and its validation rules |
| `src/gcam_emissions/factors/catalog.py` | emission-factor catalog build and validation |
| `src/gcam_emissions/factors/capss_handbook.py` | CAPSS Handbook VII PDF extraction |
| `src/gcam_emissions/factors/kaist_target.py` | reproducibly fill and audit the 135-row Korea EF target |
| `src/gcam_emissions/spatial.py` | mass to administrative shares and coordinates |
| `src/gcam_emissions/merge_scenarios.py` | combine per-scenario projections |
| `src/gcam_emissions/reference/` | packaged reference tables (the actual mapping) |
| `docs/references/emission_factor_validation/` | Korean EF literature, transcribed benchmarks, and checksums |
| `docs/figures/` | figures and their plotted data for the GCAM non-CO2 investigation; regenerate with `docs/figures/make_figures.py` |
| `paper/` | self-contained LaTeX draft of the NZK paper (Overleaf-ready); build with `pdflatex main.tex` twice from inside `paper/`. `paper/Figures/` holds copies of the investigation PNGs, refreshed by `docs/figures/make_figures.py`. The two Background sections are derived from `docs/gcam_kaist_nonco2_audit.md` and `docs/gcam_nonco2_investigation.md`, which are the source of truth: edit the markdown, then update the paper |

## Use

```bash
make validate      # check the reference tables agree with each other
make inventory     # build the sector inventory and its diagnostics
make factors       # build and validate the emission-factor catalog
make fill-kaist-efs # fill the reviewed GCAM-KAIST target and emit its audit
make scrape-capss  # extract candidates from the preserved CAPSS VII manual
make test
```
