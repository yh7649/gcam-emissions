# gcam-emissions Agent Instructions

Follow these repo-specific conventions before considering any task complete:

- Always run `make format`, `make lint`, and `make test` before finishing.
- Do not hardcode absolute or machine-specific paths. Reference tables come from
  `gcam_emissions.config.paths.REFERENCE_DIR`; every generated artifact goes
  under the workspace root, which the caller sets with `GCAM_EMISSIONS_HOME`.
- The packaged tables under `src/gcam_emissions/reference/` are tracked inputs,
  not outputs. Never write to them from code — the build reads them and writes
  elsewhere. Anything under `data/`, `results/`, or `model_inputs/` is generated
  and stays untracked.
- Keep the activity, factor, and spatial legs in separate tables. A GCAM path
  maps to a physical denominator, an inventory category supplies a factor, and a
  surrogate decides placement. These answer different questions; never collapse
  them into one column.
- Never let a missing factor become zero. Unmapped or unapproved rows belong in
  the gap tables, with their status preserved.
- Never promote a row to `production_ready=true` without a human review record.
  Nothing in the packaged catalog is approved today, and screening output must
  keep saying so.
- Purchased electricity never receives a direct emission factor. Rows marked
  `electricity_only=true` carry `direct_emissions_scope=none_on_site` and
  `not_applicable` crosswalk rows; their upstream emissions belong to the power
  sector.
- Do not leave superseded scripts or outputs lying around silently. Delete them
  or move them somewhere clearly labeled as archived, and say so in the summary.
- Keep docs in sync with structure changes. New top-level directories go in the
  README layout table; new reference tables go in `docs/reference_tables.md`.

This package is consumed by [NZK-APHIAM](../NZK-APHIAM), which installs it and
runs InMAP and the health module on its output. A change to the reference table
schemas or to any public function signature is a breaking change for that
consumer — check it before shipping.

Open work is tracked in [`docs/roadmap.md`](docs/roadmap.md).
