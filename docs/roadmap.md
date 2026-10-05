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

### Pending: rerun the power policy experiment with KEPCO factors

The power leg of the policy experiment (investigation §4, Figure 8) compares
2050 NOx/SOx avoided by `nz` vs `ref` under four factor sets. Its fourth set,
the 2017 official MOTIE factors (coal NOx/SOx 0.291/0.258 kg/MWh), is too high
for current Korean coal and is to be replaced by KEPCO's 2021
generation-weighted factors from NZK-APHIAM
(`docs/references/thermal/kepco_ef_external_validation.md`):

| kg/MWh | NOx | SOx |
|---|---|---|
| Coal (conventional steam) | 0.126 | 0.139 |
| Gas combined cycle (also applied to steam/CT) | 0.164 | 0.000 |
| Oil (conventional steam) | 0.301 | 0.011 |

Keep the Lee et al. 2022 coal-fleet variant; biomass stays at GCAM native.

Not done yet: the experiment script
(`results/diagnostics/policy_experiment/policy_experiment.py`) and the
GCAM-KAIST databases are untracked and were not available, so this needs to be
rerun locally. An estimate from the saved outputs in
`docs/figures/data/fig08_policy_power.csv` (2050 `ref` coal generation,
101.0 TWh, is recovered exactly from the two Korean variants; gas and oil are
bounded) gives about 29.5–29.8 kt NOx avoided (≈4.0× native) and
14.0–14.5 kt SOx (≈5.1–5.3×), so the headline range moves from 2.6–9.7× to
about 2.6–5.3×. The PI deck already shows these marked as estimates.

After the rerun, update: `docs/figures/data/fig08_policy_power.csv` and the
figure (`docs/figures/make_figures.py`, including its `korea_2017` label), the
power tables and "2.6–9.7×" claims in `docs/gcam_nonco2_investigation.md` and
`paper/sections/background_investigation.tex`, `paper/Figures/fig08_policy_power.png`,
and the deck's power slide.

### Pending: a consistent steel comparison

The steel leg of the policy experiment fills only the untagged routes (hydrogen DRI at the CAPSS VI
EAF factor, blast furnace with CCS at GCAM's blast-furnace factor). Every other route keeps
GCAM-KAIST's own factor, and its conventional blast furnace implies only about 0.03 kg SOx/t, so the
filled variant under-counts the reference scenario and its +19% is not a projection (investigation
§4.3). Figure 9 now shows reference vs net-zero levels under each factor set so this is visible.

To compare the scenarios fairly, apply one Korean factor set to every steel route in both scenarios:

- **Activity:** 2050 output by route for `ref` and `nz` (`BLASTFUR`, BF with CCS, `EAF with DRI`,
  hydrogen DRI, `EAF with scrap`) and steel fuel inputs, via `gcam_kaist_native_activity_crosswalk.csv`.
  These come from the untracked GCAM-KAIST databases, so this runs locally.
- **Factors available:** CAPSS VI EAF (NOx/SOx/VOCs/PM), sinter plant per tonne sinter, BOF (PM only),
  all `superseded_pending_capss_vii_diff`.
- **Factors missing:** coke-oven process factors; blast-furnace process factors; sinter and coke
  tonnes per tonne of crude steel to convert the sinter and coke factors; steel fuel-combustion
  factors by fuel. Record each as a gap until sourced; never as zero.

**Regions other than Korea.** Nothing is structurally Korea-specific in the
three-leg design, but only the CAPSS factor tables and Korean spatial inputs are
wired. GCAM-global and GCAM-USA would need their own factor and surrogate
tables.
