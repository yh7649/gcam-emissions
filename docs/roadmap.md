# Roadmap

Status as of 2026-09-07, carried over from the NZK-APHIAM extraction.

## The three legs

| Leg | Question | State |
|---|---|---|
| Activity | which GCAM path and unit gives the physical denominator | partial — 12 of 50 P1 activities have a usable conversion |
| Factor | which CAPSS category supplies the factor | mapped — 181 crosswalk rows, statuses labeled, none approved |
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

**3. No approved factors.** All 912 imported and 3,250 scraped candidates are
`production_ready=false`. The formula-heavy road and aviation-ground-equipment
tables in Handbook VII still need dedicated parsers, and every row needs human
review of source label, control status, unit, and denominator.

**4. Missing denominator conversions.** 38 of 50 P1 activities are either
blocked on a conversion (occupancy, payload, fuel density, LTO cycles) or have
no native selector at all. GCAM reports EJ and Mt; the factors want vehicle-km,
tonne-clinker, and animal-year.

## Scope not yet implemented

**Power sectors.** The intended scope covers all GCAM sectors, including
`elec_*`, the way the GCAM-USA mapping does. Only the non-power lane is ported.
NZK-APHIAM currently derives Korean power emissions from KEPCO unit-level data,
which is better than a GCAM sector-level treatment for that specific case, so
the GCAM power lane here is for generality and for regions without unit data.

**Regions other than Korea.** Nothing is structurally Korea-specific in the
three-leg design, but only the CAPSS factor tables and Korean spatial inputs are
wired. GCAM-global and GCAM-USA would need their own factor and surrogate
tables.
