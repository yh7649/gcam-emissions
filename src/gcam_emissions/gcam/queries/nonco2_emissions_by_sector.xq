(:
  Extract native non-CO2 emissions for every sector-bearing element (supplysector,
  AgSupplySector, pass-through-sector, energy-final-demand, resource extraction) in
  a GCAM-KAIST scenario database, at the technology/pollutant/year grain.

  Unlike xml_extract.py, this reads a BaseX-indexed scenario database rather than a
  flat XML/zip archive. GCAM-KAIST scenario output here ships pre-indexed as BaseX
  databases (see the "nz"/"ref" pair under model_inputs/gcam/gcam_kaist), not as the
  KAIST_9_NZ_u0902v3.xml.zip archive xml_extract.py otherwise expects.

  Setup (one-time): register a scenario export in BaseX's DBPATH, e.g.
    ln -s /path/to/model_inputs/gcam/gcam_kaist/nz  $(basex -c "XQUERY db:system()" | ...)/nz
  or copy/create it directly with `CREATE DB nz <path-to-xml>`. `basex -c "LIST"`
  confirms what is registered.

  Run (one invocation per scenario database):
    basex -b scenario-label=nz  nonco2_emissions_by_sector.xq > nz_nonco2_by_sector.csv
    basex -b scenario-label=ref nonco2_emissions_by_sector.xq > ref_nonco2_by_sector.csv

  Optionally restrict to specific model years with -b years=2015,2021 (comma-separated,
  no spaces; empty/unset means every year present in the database).

  Output columns:
    scenario, region, sector_type, sector, subsector_type, subsector,
    technology_type, technology, native_pollutant, year, native_emissions,
    native_emissions_unit

  Notes:
  - Units are native (mostly Tg, some Gg for F-gases/SF6, and MTC for CO2_FUG --
    fugitive CO2 tracked under the Non-CO2 tag, a different physical quantity from
    the species-mass units and NOT comparable to them without care).
  - `sector_type = "resource"` rows are fugitive emissions from resource extraction
    (e.g. coal-mining CH4), not supplysector output -- kept distinct on purpose.
  - This is a validation/screening lane like the rest of the native GCAM interface:
    not approved Korean activity-times-EF emissions. See native.py and AGENTS.md.
:)

declare variable $region-name external := 'South Korea';
declare variable $scenario-label external;
declare variable $years external := '';

declare function local:nearest-name($node as node(), $tags as xs:string*) as xs:string {
  let $anc := ($node/ancestor::*[local-name() = $tags])[last()]
  return if (exists($anc)) then string($anc/@name) else ''
};
declare function local:nearest-type($node as node(), $tags as xs:string*) as xs:string {
  let $anc := ($node/ancestor::*[local-name() = $tags])[last()]
  return if (exists($anc)) then local-name($anc) else ''
};

let $sector-tags := ('supplysector', 'AgSupplySector', 'pass-through-sector', 'energy-final-demand', 'resource')
let $subsector-tags := ('subsector', 'AgSupplySubsector', 'tranSubsector', 'nesting-subsector',
                         'subresource', 'reserve-subresource', 'sub-renewable-resource')
let $tech-tags := ('technology', 'AgProductionTechnology', 'tranTechnology', 'pass-through-technology',
                    'UnmanagedLandTechnology', 'intermittent-technology', 'resource-reserve-technology')
let $year-filter := if ($years = '') then () else tokenize($years, ',')
let $header := 'scenario,region,sector_type,sector,subsector_type,subsector,technology_type,technology,native_pollutant,year,native_emissions,native_emissions_unit'
let $rows :=
  for $e in db:get($scenario-label)//region[@name = $region-name]//Non-CO2/emissions
  let $year := if ($e/@year) then string($e/@year) else string($e/@vintage)
  where empty($year-filter) or $year = $year-filter
  let $pollutant := string($e/../@name)
  let $unit := string($e/@unit)
  let $value := string($e)
  let $sector := local:nearest-name($e, $sector-tags)
  let $sector-type := local:nearest-type($e, $sector-tags)
  let $subsector := local:nearest-name($e, $subsector-tags)
  let $subsector-type := local:nearest-type($e, $subsector-tags)
  let $technology := local:nearest-name($e, $tech-tags)
  let $technology-type := local:nearest-type($e, $tech-tags)
  return string-join((
    $scenario-label, $region-name, $sector-type, $sector, $subsector-type, $subsector,
    $technology-type, $technology, $pollutant, $year, $value, $unit
  ) ! replace(., ',', ';'), ',')
return string-join(($header, $rows), '
')
