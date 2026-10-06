# How GCAM-KAIST stores and reports non-CO2 emissions: an audit

Status as of 2026-10-05. Scope: the South Korea region of the two GCAM-KAIST scenario databases,
`KAIST_9_ref_u0902v3` (`ref`) and `KAIST_9_NZ_u0902v3` (`nz`). This is a screening audit. Nothing in it
is a reviewed or production-ready input.

The document has two parts:

- **Part A** explains, in plain language, what a GCAM-KAIST non-CO2 number is made of and what we found.
- **Part B** gives the technical detail and evidence behind every statement in Part A.

Where a statement is an inference rather than something read directly from the data, it is marked
**Inferred**.

---

## Part A: Plain-language guide

### A1. The units a non-CO2 number is built from

Every non-CO2 emission value GCAM-KAIST reports belongs to exactly one combination of the following:

| Unit | What it is | Example |
|---|---|---|
| Scenario | One model run | `ref`, `nz` |
| Region | Geographic unit | South Korea |
| Sector | Something GCAM produces or supplies | `electricity`, `process heat cement`, `trn_pass_road_LDV_4W` (cars and large cars) |
| Subsector | A group inside a sector, usually by fuel or vehicle type | `gas`, `coal`, `Car` |
| Technology | One specific way of producing the sector's output | `gas (CC)` (combined-cycle gas plant), `Liquids` (petrol/diesel car) |
| Vintage | The year a piece of equipment was built | the 2021-built `gas (CC)` fleet |
| Model year | The year being reported | 2015, 2021, 2050 |
| Pollutant | The emitted species | `NOx`, `SO2_2` (sulfur dioxide), `NH3` |

On top of these units sit four ideas.

**Activity.** Every technology has activity in every model year: what it produces (its *output*, for
example exajoules (EJ) of electricity, megatonnes (Mt) of cement, or billions of passenger-km) and what
it consumes (its *inputs*, for example EJ of coal).

**Non-CO2 tag.** A non-CO2 emission exists only where the model attaches an emissions object to a
technology, one per pollutant. In the database this is an element called `Non-CO2` (for example
`<Non-CO2 name="NOx">`). In the model output the tag holds **only one thing: an emission mass for each
model year**. It does not hold an emission factor, the activity it is tied to, or anything about
pollution-control equipment.

> If a technology has no tag for a pollutant, GCAM-KAIST reports nothing for it. Not zero: the
> technology simply never appears in any non-CO2 output.

**Driver.** Each tag is tied to one activity quantity, called its driver. In the GCAM input files the
driver is either a named fuel input (coal burned in a cement kiln, petrol burned by cars) or the
technology's output (electricity generated, tonnes of steel, tonnes of meat).

**Emission factor (coefficient).** The tag's mass divided by its driver: for example kilograms of NOx per
gigajoule (GJ) of coal burned, or per megawatt-hour (MWh) generated. **The model output does not store
this number.** We calculate it, and call it the *implied* coefficient.

Two more details matter when reading the data.

**Vintages.** In the historical years each technology has one vintage. In future years older equipment
keeps running alongside new equipment, and the database lists a separate tag value for each vintage.
For example, the NOx tag on coal burned for cement-kiln heat has 3 vintage entries in 2030 and 7 in
2050. A technology's total for a year is the sum over its vintages.

**Model years.** GCAM's base (calibration) years are 1975, 1990, 2005, 2010, 2015 and 2021. Future
model years in these runs are 2025 to 2050 in 5-year steps. Technologies are listed out to 2100, but
carry no output after 2050.

#### Worked example

`ref`, 2021, technology `coal` in subsector `coal` of sector `process heat cement` (coal burned to heat
cement kilns):

| Quantity | Value |
|---|---|
| Driver: coal input (`delivered coal`) | 0.0835 EJ |
| NOx tag | 0.0220 Tg (22.0 kt) |
| Implied coefficient = tag ÷ driver | 0.264 kg NOx per GJ of coal |

#### Unit conversions used in this document

| From | To |
|---|---|
| 1 Tg (teragram) | 1,000 kt = 1 million tonnes |
| 1 EJ (exajoule) | 10⁹ GJ = 2.778 × 10⁸ MWh |
| Tg per EJ | kg per GJ |
| Tg per EJ of electricity | × 3.6 → kg per MWh |
| Tg per Mt | 1,000 kg per tonne |

### A2. How a number gets into a tag

There are two phases.

**Base years (up to 2021): the mass is given.** For most sectors, GCAM's input data supplies a total
emission mass for each technology, pollutant and year. GCAM then divides that mass by its own modelled
activity for the technology to get the coefficient. The coefficient is not measured or looked up; it is
whatever is left after the division.

For a few sectors (iron and steel, fuel extraction, and two crop residue-burning species) the input data
gives the coefficient directly instead.

**Future years (2025 to 2050): emissions = coefficient × activity.** The coefficient is either kept at
its 2021 value or reduced along a pre-set curve. In the stock GCAM inputs, that curve is tied to GDP.
Almost all coefficients are the same in both scenarios, so what differs between `ref` and `nz` is mainly
the activity.

### A3. What we found

1. **Only tagged technologies report, and some large activities have no tags.** All fossil power plants
   in operation are tagged. But several large activities are not:
   - **Cement making.** Only the fuel burned for kiln heat is tagged; the kiln process itself is not.
     Paper, food processing and chemicals are the same: fuel only.
   - **Oil refining.** No tag at all, despite 4.69 EJ of output in 2021.
   - **Chemical feedstocks and industrial cogeneration.**
   - **Several technologies that grow in the net-zero scenario:** hybrid vehicles, hydrogen-based
     steel, and steel and cement with carbon capture. These show zero emissions even though, for
     example, hydrogen-based steel still burns gas and oil.
2. **For most sectors, base-year numbers are inventory numbers, not model results.** They reach
   GCAM-KAIST in four steps:
   1. **CAPSS.** Korea's National Institute of Environmental Research (NIER) estimates national
      emissions source by source. Example: 200,384 t of agricultural NH3 in 2021.
   2. **CEDS.** The Community Emissions Data System makes its own estimates for every country, then
      rescales them to match national inventories where available. For South Korea, CEDS's code reads
      the CAPSS inventory and rescales its Korean estimates so that each of its sector groups adds up to
      the CAPSS total. This covers SO2, NOx, CO, VOCs and NH3; for BC and OC it covers road transport
      only.
   3. **Stock GCAM.** GCAM's data pipeline takes the CEDS totals, divides them among GCAM's
      technologies, and stores each piece as that technology's base-year emission mass. Dividing by
      GCAM's own activity then gives the emission factor.
   4. **GCAM-KAIST.** It keeps stock GCAM's base-year numbers almost unchanged: 2,244 of 2,251 checked
      values match within 0.1%.

   Some examples of what survives the trip:
   - **Agricultural NH3 arrives intact.** CAPSS reports 200,384 t for 2021; GCAM-KAIST reports
     200,384.0 t. Agriculture lines up cleanly across CAPSS, CEDS and GCAM, so the total passes
     through unchanged.
   - **Road-transport NOx in 2021 also arrives intact:** 287,279 t in CAPSS, 287,340.6 t in GCAM-KAIST.
   - **Black carbon from power plants, factories and buildings doesn't.** CEDS rescales Korean BC for
     road transport only, so GCAM-KAIST's BC in those categories is 9–65× CAPSS's, while road BC
     matches.
   - **Gas power shows what the last step does.** GCAM receives one total for gas-fired generation and
     divides it between combined-cycle and steam/turbine plants in proportion to the gas they burn, so
     both get the same factor (B6.2). The inventory says how much the sector emitted, not which
     technology emitted it.

   Eleven GCAM-KAIST totals reproduce CAPSS category totals to within 0.12%. Two qualifications:
   - CEDS rescales by sector *group*, so exact agreement appears only where a group lines up with a
     CAPSS category.
   - Every CEDS release recent enough for GCAM's 2021 base year also rescales Korea a second time, to
     another inventory (EDGAR-HTAP), for 2000–2018. That second step doesn't touch 2021, but it does
     cover 2015 (B5.3).
3. **Technologies inside the same inventory total share one coefficient.** Because the coefficient is a
   by-product of dividing a total, distinct technologies end up with the same value:
   - combined-cycle and steam/turbine gas plants have identical coefficients per unit of fuel in every
     base year from 2005 to 2021;
   - commercial heating, cooling and "other" uses of gas share one coefficient;
   - all ten household income groups share one coefficient;
   - mobile and stationary machinery in agriculture, construction and mining carry exactly equal masses
     in every base year from 2005 to 2021.
4. **Some emissions are not tied to any activity.** Industrial process, solvent and waste emissions are
   attached to a fixed placeholder, not to production. In 2021 these placeholder-driven tags hold 81% of
   GCAM-KAIST's Korean VOCs and 55% of its SO2, excluding international shipping and aviation.
5. **Base-year coefficients are unstable.** For the typical technology and pollutant, the implied
   coefficient varies by a factor of 2 between 2005 and 2021; for one in ten it varies by more than 11×.
6. **Future coefficients don't respond to policy.** From 2021 to 2050:
   - 46% of coefficients stay frozen at their 2021 value;
   - 52% decline along the pre-set curve;
   - in 2050, 93% are identical in `ref` and `nz`.
7. **No primary particulate matter.** GCAM-KAIST reports black carbon (BC) and organic carbon (OC), but
   not PM2.5, PM10 or total suspended particulates.

### A4. Glossary

| Term | Meaning |
|---|---|
| GCAM | Global Change Analysis Model (PNNL/JGCRI). GCAM-KAIST is KAIST's version of it, run here with the scenario names above. |
| Stock GCAM v9 | The standard JGCRI release, unpacked locally at `../gcam-v9`, used as the comparison baseline. |
| CEDS | Community Emissions Data System. A global historical emissions inventory; GCAM calibrates its base-year non-CO2 emissions to it. |
| CAPSS | Clean Air Policy Support System. Korea's national air pollutant emissions inventory, published by NIER (National Institute of Environmental Research). |
| Base year / calibration year | A historical model year in which GCAM is fitted to observed data (1975–2021 here). |
| Pass-through sector | A GCAM sector that only routes a flow, such as the `elec_*` sectors that choose power-plant cooling systems. |
| `_AGR`, `_AWB` | Pollutant-name suffixes: agricultural emissions (fertilizer, livestock) and agricultural waste (crop residue) burning. |
| `SO2_2` | GCAM's name for sulfur dioxide. |
| NMVOC / VOCs | Non-methane volatile organic compounds. CAPSS calls them VOCs. |
| BaseX | The XML database engine the scenario outputs are stored in. |

---

## Part B: Technical audit

### B1. Data, tools and definitions

**GCAM-KAIST outputs.**
- Two BaseX databases under `model_inputs/gcam/gcam_kaist/`, registered as `ref` and `nz`.
- Each holds one scenario: `KAIST_9_ref_u0902v3` and `KAIST_9_NZ_u0902v3`, with `date` attributes
  2026-02-09T14:37:41+09:00 and 14:39:03+09:00.
- Only the region `South Korea` is analysed.

**GCAM-KAIST inputs.** The input XMLs KAIST used to build these runs are **not available locally**. Every
statement about how GCAM-KAIST sets its tags is therefore based on its outputs, compared with stock GCAM
v9's inputs.

**Stock GCAM v9.** `../gcam-v9`, the JGCRI GCAM release. Its `input/gcamdata` R code and `extdata`
contain no reference to CAPSS or KAIST. Files used:

| File | Used for |
|---|---|
| `input/gcamdata/xml/all_energy_emissions.xml` | Energy-sector base-year tags |
| `input/gcamdata/xml/all_aglu_emissions_IRR_MGMT.xml` | Agriculture tags |
| `input/gcamdata/xml/all_unmgd_emissions.xml`, `all_protected_unmgd_emissions.xml` | Unmanaged-land tags |
| `input/gcamdata/xml/emission_factor_controls.xml` | Future-year coefficient overrides |
| `output/queries/Main_queries.xml` | Stock reporting queries |
| `input/gcamdata/R/constants.R` | Base-year definition |
| `input/gcamdata/inst/extdata/emissions/CEDS/ceds_sector_map.csv` | CEDS → GCAM sector mapping |

**CAPSS.** `docs/2015%20Emissions%20by%20Source%20Category.xlsx` and
`docs/2021%20Emissions%20by%20Source%20Category.xlsx`. These hold first-level source-category totals only,
in tonnes.

**Definitions.**
- **Active:** a technology with output above zero in at least one model year up to 2050, in either
  scenario.
- **Air-quality (AQ) species:** BC, OC, CO, NH3, NMVOC, NOx, SO2 (including their `_AGR` and `_AWB`
  variants unless stated).
- **Identical:** within 0.1% relative difference, unless stated otherwise.

### B2. How tags are stored

**Element structure.** A tag is a child of a technology element:

```xml
<technology year="2021" name="other industrial processes" type="technology">
  <output-primary name="industrial processes" type="output">
    <physical-output unit="NA" vintage="2021">0.000243714</physical-output>
  </output-primary>
  <!-- share-weight and the BC, CH4, CO, N2O, NH3, NMVOC tags omitted -->
  <Non-CO2 name="NOx" type="GHG">
    <emissions unit="Tg" year="2021">0.0390991</emissions>
  </Non-CO2>
  <input-energy name="misc emissions sources" type="input">
    <demand-physical unit="NA" vintage="2021">0.000243714</demand-physical>
    ...
```

- In the output database, the only child element of any `Non-CO2` is `emissions`. No coefficient,
  driver, control parameter or data source is stored.
- CO2 is a separate element named `CO2`. Every element with `type="GHG"` is either `CO2` or `Non-CO2`.
  In `ref`, South Korea has 23,117 `Non-CO2` and 1,676 `CO2` elements, counting each technology vintage
  separately.

**Where tags occur.** `Non-CO2` appears under exactly six element paths:

| Path (below `region`) |
|---|
| `supplysector/subsector/technology/Non-CO2` |
| `supplysector/subsector/pass-through-technology/Non-CO2` |
| `supplysector/tranSubsector/tranTechnology/Non-CO2` |
| `AgSupplySector/AgSupplySubsector/AgProductionTechnology/Non-CO2` |
| `AgSupplySector/AgSupplySubsector/UnmanagedLandTechnology/Non-CO2` |
| `resource/reserve-subresource/resource-reserve-technology/Non-CO2` |

It never appears under `pass-through-sector`, `renewresource`, `unlimited-resource`, or technologies
nested under a `nesting-subsector`.

**Units and species** (South Korea, `ref`):

| Unit | Species |
|---|---|
| Tg | BC, CH4, CO, H2, N2O, NH3, NMVOC, NOx, OC, SO2_2; CH4_AGR, N2O_AGR, NH3_AGR, NMVOC_AGR, NOx_AGR; BC_AWB, CH4_AWB, CO_AWB, H2_AWB, N2O_AWB, NH3_AWB, NMVOC_AWB, NOx_AWB, OC_AWB, SO2_2_AWB |
| Gg | C2F6, CF4, HFC125, HFC134a, HFC143a, HFC227ea, HFC23, HFC236fa, HFC32, HFC43, SF6 |
| MTC (Mt carbon) | CO2_FUG (fugitive CO2, stored under `Non-CO2`) |

There is no PM2.5, PM10 or TSP species.

**Years and vintages.**
- Technology elements repeat once per vintage, using the `year` attribute.
- Within a technology, `emissions/@year` and `physical-output/@vintage` both give the *model year*
  being reported, despite the attribute name.
- Base years have one vintage per technology. Future years have several (cement-kiln coal NOx: 3 in
  2030, 7 in 2050).
- Model years present: 1975, 1990, 2005, 2010, 2015, 2021, 2025, 2030, 2035, 2040, 2045, 2050.
  Technology elements for 2055–2100 carry only share weights.
- Stock `constants.R` defines `MODEL_BASE_YEARS` as 1975, 1990, 2005, 2010, 2015 and the final
  historical year, which is 2021 in these outputs.

**Scenario independence of base years.** For model years up to 2021, 11,519 of 11,521
technology-pollutant-year emission values are exactly equal in `nz` and `ref`. The other two differ by at
most 1 × 10⁻⁹ Tg.

### B3. How the model reports them: native queries

Stock GCAM's `output/queries/Main_queries.xml` defines five non-CO2 queries:

| Line | Query title |
|---|---|
| 4916 | `nonCO2 emissions by region` |
| 4928 | `nonCO2 emissions by sector (excluding resource production)` |
| 4934 | `nonCO2 emissions by resource production` |
| 4945 | `nonCO2 emissions by subsector (excluding resource production)` |
| 4952 | `nonCO2 emissions by tech (excluding resource production)` |

Each selects `*[@type = 'GHG' and @name != 'CO2' and @name != 'CO2_FUG']/emissions` beneath sector and/or
resource nodes. None of them names a sector.

**Consequence: there are no sector-specific non-CO2 queries.** A sector reports non-CO2 emissions if, and
only if, its technologies carry `Non-CO2` tags. "Is there a query for cement non-CO2?" reduces to "does
any cement technology carry a tag?", and the answer is no (B4).

The repo's query `src/gcam_emissions/gcam/queries/nonco2_emissions_by_sector.xq` selects every
`Non-CO2/emissions`. That is the same set of tags as the stock queries, plus `CO2_FUG`.

### B4. Coverage: which activity carries tags

**Method.** `results/diagnostics/nonco2_coverage/activity_inventory.xq` lists every technology under
`supplysector`, `AgSupplySector`, `pass-through-sector`, `resource`, `renewresource` and
`unlimited-resource`. For each it records output by year and the `Non-CO2` species it carries. The set of
tagged (sector, subsector, technology) triples it finds, 286 in total, is identical to the set in the
repo's emissions detail table.

**Counts** (active nodes only; each household income decile counts as its own sector):

| | Sectors | Subsectors |
|---|---|---|
| All active technologies tagged | 77 | 169 |
| Some active technologies tagged | 50 | 36 |
| No active technology tagged | 139 | 281 |
| **Total active** | **266** | **486** |

No tagged technology has all-zero emissions in every year up to 2050.

**Power.**
- Power tags sit on `electricity/<fuel>/<pass-through-technology>`, for example
  `electricity/gas/gas (CC)`.
- That technology's only energy input is the pass-through sector `elec_gas (CC)`, in a quantity equal to
  the electricity generated.
- The 18 `elec_*` pass-through sectors, which hold the cooling-system choices, carry no `Non-CO2` tags.
  The fossil ones carry `CO2` tags.
- Every fossil power technology with activity is tagged. The untagged fossil power technologies have zero
  output through 2050 in both scenarios: `coal (IGCC)`, `coal (conv pul CCS)`, `coal (IGCC CCS)`,
  `refined liquids (CC)`, `refined liquids (CC CCS)`, `biomass (conv CCS)` and `biomass (IGCC CCS)`.

**Active technologies with no tag that burn fuel on site or run an industrial process:**

| Sector / technology | Output unit | 2021 `ref` | 2050 `ref` | 2050 `nz` | Carries a CO2 tag |
|---|---|---|---|---|---|
| `cement` / `cement` | Mt | 50.45 | 47.87 | 6.774 | yes |
| `cement` / `cement CCS` | Mt | 0 | 0 | 30.41 | yes |
| `paper` / `paper` | Mt | 10.83 | 9.917 | 9.741 | no |
| `food processing` / `food processing` | Pcal | 59.36 | 56.43 | 56.22 | no |
| `chemical` / `chemical` | EJ | 2.422 | 3.150 | 3.026 | no |
| `chemical feedstocks` / `refined liquids` | EJ | 2.086 | 2.453 | 2.408 | yes |
| `other industry` / `other industry` | EJ | 1.090 | 1.314 | 1.289 | no |
| `construction` / `construction` | EJ | 0.0871 | 0.0850 | 0.0810 | no |
| `N fertilizer` / `N fertilizer` | Mt N | 0.2279 | 0.2058 | 0.1757 | no |
| `refining` / `oil refining` | EJ | 4.694 | 3.666 | 2.405 | yes |
| `other industrial energy use` / `coal cogen` | EJ | 0.1436 | 0.06497 | 0.00004 | yes |
| `other industrial energy use` / `gas cogen` | EJ | 0.0473 | 0.01101 | 0.0003 | yes |
| `other industrial energy use` / `refined liquids cogen` | EJ | 0.0408 | 0.00411 | 0.00002 | yes |
| `other industrial energy use` / `biomass cogen` | EJ | 0.00374 | 0.00228 | 0.00008 | yes |
| `iron and steel` / `Hydrogen-based DRI` | Mt | 0 | 10.29 | 16.36 | yes |
| `iron and steel` / `BLASTFUR CCS` | Mt | 0 | 0 | 4.150 | yes |

None of the technologies in this table has an entry in stock GCAM v9's Korea block of
`all_energy_emissions.xml`. `Hybrid Liquids` and `oil refining` have no entry for any region. These
gaps are therefore inherited from stock GCAM, not introduced by KAIST.

The fuel-combustion emissions of `cement`, `paper`, `food processing`, `chemical`, `other industry` and
`construction` *are* tagged, but on companion energy-use sectors: `process heat cement`,
`process heat paper`, `waste biomass for paper`, `process heat food processing`, `chemical energy use`,
`other industrial energy use` and `construction energy use`. What has no tag anywhere is the
non-combustion process emissions of these industries, apart from the unattributed lump in B6.4.

**Untagged technologies still burn fuel.** In `nz` 2050:
- `Hydrogen-based DRI` consumes 0.0428 EJ of `wholesale gas` and 0.0180 EJ of
  `refined liquids industrial`, as well as hydrogen and electricity.
- `BLASTFUR CCS` consumes 0.0617 EJ of `delivered coal` and 0.0238 EJ of `wholesale gas`.

**Hybrid vehicles** (`Hybrid Liquids`) have no tags in any mode:

| Sector / subsector | Unit | 2050 `ref` | 2050 `nz` |
|---|---|---|---|
| `trn_pass_road` / `Bus` | billion passenger-km | 108.9 | 78.02 |
| `trn_pass_road_LDV_4W` / `Car` | billion passenger-km | 42.91 | 19.16 |
| `trn_pass_road_LDV_4W` / `Large Car and Truck` | billion passenger-km | 35.54 | 18.13 |
| `trn_freight_road` / `Medium truck` | billion tonne-km | 6.587 | 3.587 |
| `trn_freight` / `Freight Rail` | billion tonne-km | 4.404 | 0.644 |
| `trn_freight` / `Domestic Ship` | billion tonne-km | 24.18 | 0 |
| `trn_shipping_intl` / `International Ship` | billion tonne-km | 2,837 | 0.058 |

**Tags with no air-quality species** (greenhouse gases, fluorinated gases or hydrogen only):

| Sector / subsector | Species |
|---|---|
| `comm cooling`, `resid cooling modern_d1`–`_d10` / `electricity` | HFC125, HFC134a, HFC143a, HFC23, HFC32 |
| `electricity_net_ownuse` | SF6 |
| `industrial processes` / `Al_Mg` | SF6 |
| `industrial processes` / `HCFC_22_Prod` | HFC23 |
| `industrial processes` / `adipic acid`, `nitric acid` | N2O |
| `industrial processes` / `semiconductors` | C2F6, CF4, HFC23, SF6 |
| `urban processes` / `fire_exting` | HFC227ea, HFC236fa |
| `H2 LDV`, `H2 MHDV`, `LH2`, `H2 liquid truck`, `H2 pipeline` (delivery) | H2 |
| `biomass` (bioenergy crops) | N2O_AGR |

Two hydrofluorocarbon (HFC) sources, `industrial processes / foams` and `urban processes / aerosols`,
are active but carry no tag at all.

**The remaining untagged active nodes** are markets, trade nodes, aggregators, fuel distribution,
water supply, labor and capital, renewable and nuclear supply, and electricity-, hydrogen- or
human-powered end uses. The full list, with a reason for each, is in
`gcam_kaist_nonco2_coverage_by_subsector.csv`. Those reasons are our screening judgment and have not been
reviewed.

### B5. Where base-year values come from

#### B5.1 Two ways of specifying a tag in stock GCAM

In stock GCAM v9's inputs, each base-year `Non-CO2` entry is specified in one of two ways:

- `<input-emissions>`: a mass. The coefficient is derived from it.
- `<emiss-coef>`: a coefficient, given directly.

Each entry also declares a driver: `<input-driver><input-name>…</input-name></input-driver>` for a named
input, or `<output-driver/>` for the technology's output. For South Korea in 2015 and 2021:

| Sectors | Specified as | Driver |
|---|---|---|
| `electricity` | mass | output |
| `industrial processes`, `urban processes` | mass | output |
| Livestock (`Beef`, `Dairy`, `Pork`, `Poultry`, `SheepGoat`) | mass | output |
| Crops (`_AGR` species) | mass | output |
| Crops (`BC_AWB`, `OC_AWB`) | coefficient | output |
| `UnmanagedLand` | mass | input `land-input` |
| Buildings (`comm *`, `resid *`) | mass | named fuel input |
| Transport (`trn_*`) | mass | named fuel input |
| Industrial energy (`chemical energy use`, `other industrial energy use`, `process heat *`, `ammonia`, `waste biomass for paper`) | mass | named fuel input |
| `agricultural energy use`, `construction energy use`, `mining energy use` | mass | named fuel input |
| `iron and steel` | coefficient | output |
| Fuel resources (`coal`, `crude oil`, `natural gas`) | coefficient | output |

The other `_AWB` species that appear in GCAM-KAIST's outputs (for example `CO_AWB`, `NOx_AWB`) were not
found in the stock files examined, so how they are specified is unknown.

Stock inputs also attach a `gdp-control` element (with `max-reduction` and `steepness`) to many entries.
`emission_factor_controls.xml` overrides some future coefficients directly. For example, for South Korea
the international shipping SO2 coefficient is 0.16 in 2020, falling to 0.13 by 2050, and its GDP control
is deleted.

#### B5.2 GCAM-KAIST compared with stock GCAM v9

Extraction: `results/diagnostics/capss_calibration_test/stock_korea2.py`.

**Mass-specified tags, 2015 and 2021, AQ species.**

| | Cells |
|---|---|
| Present in both, identical within 0.1% | 2,244 |
| Present in both, different | 7 |
| **Present in both, total** | **2,251** |

The seven differing cells are `UnmanagedLand` rows in 2015. Beyond them:
- **In stock, absent from GCAM-KAIST:** `chemical energy use / gas` in 2015, 8.04 kt summed over AQ
  species, plus small agricultural- and mining-stationary entries.
- **In GCAM-KAIST, absent from the stock files examined:** unmanaged-land fire subsectors (12.5 kt over
  2015 and 2021).
- **In GCAM-KAIST, carried forward from a stock 1975 coefficient:** `refining / biomass liquids /
  biodiesel` (1.40 kt over 2015 and 2021). Stock GCAM sets biodiesel only in 1975, as a coefficient per
  EJ of `regional biomassOil` input: 0.01 Tg/EJ for SO2, NOx and CO alike, and 0.0001 for N2O and NMVOC.
  GCAM-KAIST's 2015 and 2021 biodiesel emissions equal that coefficient times the biodiesel's
  `regional biomassOil` input, to five significant figures.

**Coefficient-specified tags.** For `iron and steel` and the `coal`, `crude oil` and `natural gas`
resources, GCAM-KAIST's implied coefficient (emissions ÷ output) equals the stock `emiss-coef` to within
0.001%. This holds for NOx, SO2, CO and NMVOC in 2015 and 2021.

**Conclusion.** In the base years, GCAM-KAIST's non-CO2 emissions for South Korea are, with the small
exceptions listed, stock GCAM v9's.

#### B5.3 Upstream of stock GCAM: CEDS and CAPSS

**GCAM → CEDS.** GCAM's base-year non-CO2 emissions are calibrated to CEDS. `ceds_sector_map.csv`
maps CEDS sectors to GCAM sector groups. For example `1A1a_Electricity-public` → `elec_heat`, and
`1A1bc_Other-transformation` → `industry_energy`. GCAM v9 ships its CEDS-derived results as prebuilt
data. The raw CEDS files are not included locally (the gcamdata code describes them as proprietary),
and the CEDS release used is not recorded.

**CEDS → CAPSS.** CEDS's code (<https://github.com/JGCRI/CEDS>, checked 2026-10-05) carries the CAPSS
inventory and scales its Korean estimates to it:

| CEDS file | Role |
|---|---|
| `input/emissions-inventories/Korea/Korea_CAPSS_Emissions.xlsx` | The CAPSS inventory, stored in CEDS |
| `code/module-E/E.South_Korea_emissions.R` | Reads it as the inventory `Korea_CAPSS_Emissions` |
| `code/module-F/F1.1.South_Korea_scaling.R` | Scales CEDS's default Korea estimates to CAPSS by sector (`mapping_method <- 'sector'`, replacement method `replace`): SO2, NOx, CO, NMVOC and NH3 for 1999–2021; BC and OC for 2011–2021 |
| `input/mappings/scaling/South_Korea_BCOC_scaling_method.csv` | Lists only `1A3b_Road` for Korea, so BC and OC are scaled for road transport only |

This scaling step is present, with these parameters, in the v_2024_07_08 release. The CEDS README
also notes that the April 2021 release (v_2021_04_21) updated emissions for South Korea specifically.

**A second scaling step (EDGAR-HTAP).** Immediately after the CAPSS step, CEDS's scaling driver
(`code/module-F/F1.inventory_scaling.R`) rescales Korea again, by sector with replacement, to the
EDGAR-HTAP inventory for 2000–2018:
- In v_2024_04_01 and v_2024_07_08 this is `F1.1.South_Korea_EDGAR-HTAPv3_scaling.R`, run for CO,
  NH3, NMVOC, NOx and SO2.
- In the current code it is `F1.1.South_Korea_EDGAR-HTAPv3.1_scaling.R`, first committed with the
  v_2025_03_18 release.

**Which release GCAM v9 used (Inferred).** It is not recorded. But the v_2021_04_21 release has data
only to 2019 (`BP_last_year <- 2019` in `code/parameters/common_data.R`), so it cannot supply GCAM's
2021 base year. GCAM v9 must therefore use v_2024_04_01 or later, and every such release includes
both Korean scaling steps.

**Consequences for the comparison with CAPSS.**
- 2021 lies outside the EDGAR-HTAP window, so GCAM-KAIST's 2021 Korean values are scaled to CAPSS
  only.
- 2015 lies inside it. Several 2015 cells still match CAPSS almost exactly: agricultural NH3, road
  SOx and VOCs, waste SOx, and industrial-process NH3. But road NOx in 2015 is 25% above CAPSS while
  matching in 2021. Whether the second step explains such differences was not determined.
- Because scaling is by sector group, exact agreement is expected only where a CEDS scaling group
  maps cleanly onto a CAPSS category (B5.4).

**Not verified here:**
- the exact CEDS release in GCAM v9;
- CEDS's Korean scaling-sector definitions, and how they line up with CAPSS categories;
- how EDGAR-HTAP's Korean values relate to CAPSS.

#### B5.4 Agreement with CAPSS

GCAM-KAIST emissions were assigned to CAPSS first-level categories using the repo crosswalk
(`src/gcam_emissions/reference/gcam_kaist_capss_category_crosswalk.csv`) plus the two overrides in
`capss_category_comparison.py`: `_AWB` → Biomass burning, and `industrial processes/solvents` → Solvent
use. Eleven category × pollutant × year cells agree with CAPSS to within 0.12%:

| CAPSS category | Pollutant | Year | CAPSS (t) | GCAM-KAIST (t) |
|---|---|---|---|---|
| Agriculture | NH3 | 2015 | 231,263 | 231,263.0 |
| Agriculture | NH3 | 2021 | 200,384 | 200,384.0 |
| Road transport | NOx | 2021 | 287,279 | 287,340.6 |
| Road transport | SOx | 2015 | 209 | 208.8 |
| Road transport | SOx | 2021 | 248 | 248.0 |
| Road transport | NH3 | 2021 | 1,706 | 1,706.6 |
| Road transport | VOCs | 2015 | 46,145 | 46,146.7 |
| Industrial process | NH3 | 2015 | 39,432 | 39,467.3 |
| Industrial process | NH3 | 2021 | 41,953 | 41,991.1 |
| Waste disposal | SOx | 2015 | 2,119 | 2,119.1 |
| Waste disposal | SOx | 2021 | 1,382 | 1,383.5 |

All eleven cells come from mass-specified tags (B5.1). The same values are present in stock GCAM v9
(B5.2).

Other cells agree much less well. BC, for example, differs by large factors in the stationary-combustion
categories while agreeing closely in Road transport and Biomass burning:

| CAPSS category | BC ratio GCAM-KAIST / CAPSS, 2015 | 2021 |
|---|---|---|
| Energy production | 8.9 | 11.1 |
| Manufacturing industry | 10.1 | 36.8 |
| Non-industry | 65.4 | 17.5 |
| Waste disposal | 37.8 | 28.4 |
| Road transport | 1.0 | 1.0 |
| Biomass burning | 1.0 | 0.9 |

Road transport is the only sector where CEDS scales Korean BC to CAPSS (B5.3), which fits its ratio of
1.0.

**Inferred.** Agreement to four or five significant figures cannot arise from independent estimation.
Together with B5.2 and B5.3, it indicates that these base-year values are CAPSS totals, passed through
CEDS into GCAM's calibration and divided among GCAM technologies.

#### B5.5 Where refinery emissions sit (Inferred)

`oil refining` has no tag (B4). CEDS sector `1A1bc_Other-transformation`, which includes petroleum
refining, is mapped to GCAM's `industry_energy` group (B5.3).

The comparison tested reassigning `other industrial energy use / refined liquids` from Manufacturing
industry to Energy production (CAPSS's Energy production includes refineries). This was done together
with moving `refining / biomass liquids`, under 0.3 kt per pollutant, the other way. The result:
- Energy production CO and NH3 come within 2.0% of CAPSS in both years. NH3 in 2015 is 1,378.2 t vs
  1,379 t.
- Energy production VOCs come within 2.3% (2015) and 6.1% (2021).
- Manufacturing industry CO in 2021 moves from 85% above CAPSS to 3.6% above.

This indicates that refinery fuel-combustion emissions are stored in
`other industrial energy use / refined liquids`, not in `refining`.

### B6. Implied coefficients

#### B6.1 Method

`results/diagnostics/nonco2_coverage/driver_consistent_coef.py` computes each coefficient as follows:
- **Numerator:** the tag's emissions, summed over vintages.
- **Denominator:** the driver stock GCAM declares for that tag (B5.1). That is the named fuel input
  (`demand-physical`) or the technology's output (`physical-output`).
- **Included tags:** only mass-specified tags.
- **Deciles:** income deciles `_d2`–`_d10` are dropped because they duplicate `_d1` (shown below).
- **Pollutants:** NOx, SO2, NMVOC, NH3, CO, BC and OC (no `_AGR` or `_AWB`).

#### B6.2 Distinct technologies with the same coefficient

**Gas power: combined cycle vs steam/turbine.**
- Per unit of fuel burned, `gas (CC)` and `gas (steam/CT)` have identical coefficients in every base
  year from 2005 to 2021. The fuel burned is the gas input to the matching `elec_*` sector.
- The stock 2021 masses (0.006297 and 0.001779 Tg NOx) are in the same ratio, 3.54, as the two
  technologies' gas use (0.9943 and 0.2809 EJ).
- Per MWh generated, the coefficients differ only by the efficiency ratio: 0.0404 vs 0.0605 kg/MWh NOx in
  2021.
- The two diverge only after 2021.

| kg per TJ of gas | 2005 | 2010 | 2015 | 2021 | 2030 | 2050 |
|---|---|---|---|---|---|---|
| NOx, `gas (CC)` | 95.01 | 19.46 | 21.10 | 6.33 | 5.02 | 4.60 |
| NOx, `gas (steam/CT)` | 95.01 | 19.46 | 21.10 | 6.33 | 3.34 | 2.05 |
| CO, `gas (CC)` | 28.99 | 44.91 | 56.21 | 38.25 | 19.20 | 11.30 |
| CO, `gas (steam/CT)` | 28.99 | 44.91 | 56.21 | 38.25 | 20.17 | 12.04 |

**Inferred.** The gas-power total was divided between the two technologies in proportion to fuel use,
not according to technology-specific emission rates.

**Buildings.**
- *Same coefficient across services.* In 2015 and 2021, `comm cooling`, `comm heating` and
  `comm others` have the same coefficient per unit of gas for every pollutant (NOx in 2021: 67.45 kg/TJ).
  `resid heating` and `resid others` match each other for coal, gas and refined liquids (checked in
  2021; gas NOx: 62.26 kg/TJ).
- *Same coefficient across income deciles.* Across the ten income deciles, coefficients differ by at most
  0.09%.

**Non-road machinery: equal masses.** In `agricultural energy use`, `construction energy use` and
`mining energy use`, the `refined liquids` technology carries **exactly the same mass** in subsector
`mobile` and subsector `stationary`. This holds in every base year (2005, 2010, 2015, 2021) and for every
pollutant checked (NOx, CO, SO2). The equal masses are already present in stock GCAM v9's inputs
(checked for agricultural and construction NOx in 2015 and 2021).

| 2021, kt | NOx, mobile | NOx, stationary |
|---|---|---|
| `agricultural energy use` | 12.296 | 12.296 |
| `construction energy use` | 31.103 | 31.103 |
| `mining energy use` | 0.108 | 0.108 |

**Steel: EAF routes.** The stock coefficients themselves give electric-arc-furnace steel made from
direct-reduced iron (`EAF with DRI`) a far higher NOx coefficient than EAF steel made from scrap
(`EAF with scrap`):

| NOx, kg per tonne of steel | 2015 | 2021 |
|---|---|---|
| `EAF with DRI` | 0.778 | 11.66 |
| `EAF with scrap` | 0.134 | 0.216 |
| `BLASTFUR` (blast furnace) | 1.092 | 0.478 |

In 2021 this gives the two EAF routes nearly equal NOx masses (4.67 and 4.75 kt), although their outputs
are 0.400 and 21.98 Mt.

#### B6.3 Base-year instability

Across the 436 mass-specified technology-pollutant series with a positive coefficient in all four of
2005, 2010, 2015 and 2021 (deciles collapsed, `ref`), the ratio of the largest to the smallest coefficient
is:

| Statistic | Value |
|---|---|
| Median | 2.04 |
| Share above 1.5× | 69% |
| Share above 2× | 52% |
| 90th percentile | 11.6 |
| Maximum | 134.7 (OC from residential coal heating) |

Examples:

| Coefficient | 2005 | 2010 | 2015 | 2021 |
|---|---|---|---|---|
| Coal power (`coal (conv pul)`) NOx, kg/MWh | 1.753 | 0.509 | 0.458 | 0.150 |
| Coal power SO2, kg/MWh | 0.408 | 0.214 | 0.267 | 0.071 |
| Gas combined-cycle (`gas (CC)`) NOx, kg/MWh | 0.684 | 0.124 | 0.134 | 0.040 |
| Oil power (`refined liquids (steam/CT)`) SO2, kg/MWh | 0.395 | 0.424 | 0.521 | 0.374 |
| Cement-kiln coal NOx, kg/GJ coal | 0.318 | 0.346 | 0.247 | 0.264 |
| Commercial gas (`comm others`) NOx, kg/GJ gas | 0.0366 | 0.0402 | 0.0416 | 0.0674 |
| Car petrol/diesel (`Liquids`) NOx, kg/GJ fuel | 0.229 | 0.117 | 0.119 | 0.072 |

**Inferred.** For mass-specified tags, each base-year coefficient equals the inventory mass divided by
GCAM's modelled activity, so any difference between GCAM's activity and the activity behind the
inventory is absorbed into the coefficient.

#### B6.4 Placeholder-driven tags

Every tagged subsector of `industrial processes` and `urban processes` takes `misc emissions sources`,
an `unlimited-resource`, as input. Stock GCAM declares an output driver for these tags.
That output is a fixed placeholder (unit `NA`), not a production quantity:
- In 2021 all eight `industrial processes` subsectors output 0.000243714.
- The `urban processes` subsectors output 0.0008.

The NOx and SO2 on `industrial processes / other industrial processes` fall from 2021 to 2050 almost
identically in both scenarios:

| `other industrial processes` | 2021 | 2050 `ref` | 2050 `nz` |
|---|---|---|---|
| NOx, kt | 39.10 | 13.62 | 13.36 |
| SO2, kt | 83.81 | 29.19 | 28.64 |

The table below gives the share of GCAM-KAIST's 2021 Korean emissions on placeholder-driven tags. It
uses `ref` and excludes `trn_aviation_intl` and `trn_shipping_intl`.

| Pollutant | On placeholder-driven tags | Share of total |
|---|---|---|
| VOCs | 760 kt | 81% |
| SO2 | 85 kt | 55% |
| NH3 | 42 kt | 17% |
| NOx | 50 kt | 6% |
| CO | 35 kt | 6% |

The VOCs are mainly `solvents` (574 kt), `other industrial processes` (128 kt) and `landfills` (48 kt).

#### B6.5 Future years

Of 463 mass-specified series with a positive 2021 coefficient (deciles collapsed, `ref`), comparing the
2050 coefficient with the 2021 one:

| Behaviour | Series | Share |
|---|---|---|
| Frozen (within ±1%) | 213 | 46% |
| Declining | 243 | 52% |
| Rising | 7 | 2% |

Frozen series are most common in `process heat cement`, `construction energy use`, `UnmanagedLand` and
residential heating. Declining series are most common in `electricity`, `chemical energy use`,
`other industrial energy use` and cars.

In 2050, 409 of 439 coefficients (93%) are identical in `nz` and `ref`.

| Coefficient | 2021 | 2030 | 2050 | Behaviour |
|---|---|---|---|---|
| Cement-kiln coal NOx, kg/GJ | 0.264 | 0.264 | 0.264 | frozen |
| Commercial gas NOx, kg/GJ | 0.0674 | 0.0674 | 0.0674 | frozen |
| Oil power NOx, kg/MWh | 0.320 | 0.320 | 0.320 | frozen |
| Oil power SO2, kg/MWh | 0.374 | 0.193 | 0.108 | declining |
| Coal power NOx, kg/MWh | 0.150 | 0.077 | 0.043 | declining |
| Coal power SO2, kg/MWh | 0.071 | 0.037 | 0.021 | declining |
| Car petrol/diesel NOx, kg/GJ | 0.072 | 0.037 | 0.021 | declining |

The stock inputs contain the mechanisms that produce this behaviour (`gdp-control`, and future
`emiss-coef` overrides in `emission_factor_controls.xml`). For South Korea, that file sets 2025
coefficients for the six CCS power technologies (for example `gas (CC CCS)` NOx: 0.00246) and SO2
coefficients for domestic and international shipping. GCAM-KAIST's own control settings cannot be
inspected, because its input files are not available.

### B7. Summary: what the encoding can and cannot represent

| Change in a scenario | How GCAM-KAIST's non-CO2 emissions respond |
|---|---|
| Shift between tagged technologies (for example coal → gas power) | Emissions change at each technology's coefficient. |
| Shift between technologies that share a coefficient (gas CC ↔ steam/CT per unit of fuel; heating ↔ cooling ↔ other; deciles) | Base-year coefficients do not distinguish them. |
| Shift to an untagged technology (hybrid vehicles, hydrogen-based DRI, steel or cement with CCS) | Emissions of that activity are zero. |
| Change in industrial output or refinery throughput | Process emissions do not respond: they are absent, or sit on a placeholder driver. Refinery combustion follows `other industrial energy use / refined liquids` (Inferred, B5.5). |
| Pollution-control policy (scrubbers, emission standards) | No lever. Coefficients are frozen, or follow a curve shared by both scenarios. |
| Primary PM2.5 / PM10 | Not represented. |

### B8. Limitations of this audit

- **KAIST inputs.** GCAM-KAIST's input XMLs were not examined. Statements about how its tags are set
  rely on its outputs and on stock GCAM v9's inputs.
- **CEDS link.** CEDS's code confirms the scaling to CAPSS (B5.3). But the CEDS release used by GCAM
  v9 is inferred, not recorded, and the effect of CEDS's second Korea scaling step (EDGAR-HTAP,
  2000–2018) on the 2015 values was not determined.
- **Refinery location.** B5.5 is an inference from a sector map and a mapping test, not from an explicit
  source record.
- **Coefficient scope.** Implied coefficients use the driver stock GCAM declares. Where GCAM-KAIST
  declares a different driver, its true coefficient would differ.
- **Reasons for untagged nodes.** The classification of untagged active nodes (B4) is our screening
  judgment and has not been reviewed.
- **Region.** Only South Korea was examined.

### B9. Reproducing the evidence

All scripts and outputs below are local diagnostics under `results/`, which is untracked. They should be
moved into the package before this document is circulated as a reproducible record.

| Evidence | Script | Output |
|---|---|---|
| Native emissions detail (all tags) | `src/gcam_emissions/gcam/nonco2_by_sector.py` + `queries/nonco2_emissions_by_sector.xq` | `data/interim/gcam_native_emissions_by_sector/gcam_kaist_nonco2_emissions_detail.csv` |
| Activity and tag coverage (B4) | `results/diagnostics/nonco2_coverage/activity_inventory.xq` (run with `basex -b db=ref`, then `db=nz`), `build_coverage.py` | `gcam_kaist_nonco2_coverage_by_technology.csv`, `..._by_subsector.csv` |
| Activity drivers by technology | `results/diagnostics/policy_experiment/drivers.xq` | `drv_ref.csv`, `drv_nz.csv` |
| Power fuel use | `results/diagnostics/nonco2_coverage/elecfuel.xq` | `elecfuel_ref.csv`, `elecfuel_nz.csv` |
| Stock GCAM v9 Korea specifications (B5.1–B5.2) | `results/diagnostics/capss_calibration_test/stock_korea2.py` | `stock_korea2.csv` |
| CAPSS agreement (B5.4–B5.5) | `results/diagnostics/capss_calibration_test/mapping_search.py` | `capss_mapping_search_default.csv`, `..._best.csv` |
| Driver-consistent coefficients (B6.1, B6.3, B6.5) | `results/diagnostics/nonco2_coverage/driver_consistent_coef.py` | `driver_consistent_coef.csv` |
| Per-fuel power coefficients and placeholder shares (B6.2, B6.4) | `results/diagnostics/nonco2_coverage/implied_ef.py` (its sections D–E are superseded by the line above) | `implied_ef_long.csv` |

Related analyses that build on this audit, not part of it:
- the CAPSS mapping review (`results/diagnostics/nonco2_coverage/gcam_kaist_capss_mapping_review.csv`);
- the mapping search (`results/diagnostics/capss_calibration_test/`);
- the policy-sensitivity experiment (`results/diagnostics/policy_experiment/`).

### Sources

- JGCRI, *Community Emissions Data System (CEDS)*, <https://www.github.com/JGCRI/CEDS>. Files cited in
  B5.3:
  - CAPSS scaling: <https://github.com/JGCRI/CEDS/blob/master/code/module-F/F1.1.South_Korea_scaling.R>
  - BC/OC method: <https://github.com/JGCRI/CEDS/blob/master/input/mappings/scaling/South_Korea_BCOC_scaling_method.csv>
  - Scaling driver at v_2024_07_08:
    <https://github.com/JGCRI/CEDS/blob/2024_07_08_Release/code/module-F/F1.inventory_scaling.R>
  - Release notes: <https://github.com/JGCRI/CEDS/wiki/Release-Notes>
- CEDS reviewer-response supplement, ESSD preprint essd-2020-103,
  <https://essd.copernicus.org/preprints/essd-2020-103/essd-2020-103-AC1-supplement.pdf>.
- Stock GCAM v9 files listed in B1.
