# Roadmap

Status as of 2026-09-08, carried over from the NZK-APHIAM extraction.

## The three legs

| Leg | Question | State |
|---|---|---|
| Activity | which GCAM path and unit gives the physical denominator | partial — 12 of 50 P1 activities have a usable conversion |
| Factor | which CAPSS category supplies the factor | target researched — all 135 target rows carry evidence, N/A, or an explicit gap; 97 remain blocked from production use |
| Spatial | where the mass lands on the grid | not built — the coordinate interface is header-only |

## Blockers, in the order they bind

**1. Spatial surrogates.** `nonpower_spatial_geometry.csv` is header-only, so
nothing has reviewed coordinates. The current allocator falls back to placing
CAPSS administrative shares at AirKorea monitor centroids, which are where air
is measured, not where sources are. The readiness audit classifies the 50 P1
rows as 17 point-preferred, 32 grid-preferred, and 1 unresolved.

The transferable design here is the US SMOKE surrogate pattern: each source
category points at a spatial weighting layer — road network for on-road,
population for residential and commercial, industrial land use or a point-source
registry for manufacturing. Korean equivalents need to be assembled.

**2. Administrative joins run on names, not codes.** The allocator matches
`province_name_ko` and `sub_district_name_ko` as strings. Renamed or merged
시군구 will mismatch silently. An official admin-code crosswalk should be joined
before any of this is trusted.

**3. Most target assignments still need effective-factor inputs.** All 912
imported and 3,250 automatically scraped candidates remain
`production_ready=false`. The reviewed target-table workflow records 38 ready
rows (mostly no-direct-emissions decisions plus exact cement, forest-fire, and
coal-power evidence) and 97 blocked rows: 75 need denominator or technology
weights and 21 remain Korean-EF research gaps, while municipal incineration has
an exact raw factor but no target activity unit. Formula-heavy road factors are
now referenced explicitly but still need Korean fleet/speed weighting.

The source material and prior review work are now local to this repository:
see [`emission_factor_collection.md`](emission_factor_collection.md) and the
[`Korean EF evidence archive`](references/emission_factor_validation/README.md).

**4. Missing denominator conversions.** 38 of 50 P1 activities are either
blocked on a conversion (occupancy, payload, fuel density, LTO cycles) or have
no native selector at all. GCAM reports EJ and Mt; the factors want vehicle-km,
tonne-clinker, and animal-year.

## Power sectors — back in scope as of 2026-09-08

Reversed from the earlier "not yet implemented" call: KEPCO unit-level data is
better than a GCAM sector-level treatment, but it only exists for observed
years. NZK-APHIAM's MACRO power-sector model — the thing meant to project
Korean power-sector generation and emissions forward under the NZK scenario —
isn't ready. Until it is, GCAM-KAIST's own `elec_*` activity and native
emissions are the interim source for *projected* Korean power-sector emissions;
KEPCO stays authoritative for observed years.

Where this actually stands: `docs/gcam_kaist_ef_target_table.csv` carries 7
`elec_*` rows — `elec_coal (conv pul)`,
`elec_gas (CC)`, `elec_gas (CC CCS)`, `elec_gas (steam/CT)`,
`elec_biomass (IGCC)`, `elec_biomass (conv)`, `elec_refined liquids
(steam/CT)` — surfaced from the GCAM-USA-NEI sector mapping exercise. The EF
column now contains Korean official/literature factors where defensible and an
explicit gap for biomass IGCC; the CAPSS-equivalent columns remain blank. Two
structural gaps remain before power can run like non-power:

- `gcam_kaist_nonpower_sector_inventory.csv` is non-power by name and design
  (priority/`include_in_mvp`/status columns). Power sectors have no equivalent
  inventory entries yet — they need their own priority table, not a forced fit
  into the non-power one.
- Unlike most non-power P1 activities, GCAM-KAIST's power-sector activity
  needs little denominator conversion (native units — EJ, km³ — and native
  emissions are already present per fuel/technology), so this leg may be
  faster to stand up than non-power was, once the inventory entries exist.

**Regions other than Korea.** Nothing is structurally Korea-specific in the
three-leg design, but only the CAPSS factor tables and Korean spatial inputs are
wired. GCAM-global and GCAM-USA would need their own factor and surrogate
tables.
