"""Reproducibly populate the reviewed GCAM-KAIST emission-factor target table.

The target table is a research handoff rather than a normalized factor catalog.  Its
fourth column therefore records either a Korean factor/set/formula, an explicit
no-direct-emissions decision, or a visible research gap.  Missing evidence is never
written as zero.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

from gcam_emissions.config.paths import REFERENCE_DIR, RESULTS_DIAGNOSTICS_DIR, WORKSPACE_ROOT

TARGET_RELATIVE_PATH = Path("docs/gcam_kaist_ef_target_table.csv")
AUDIT_RELATIVE_PATH = Path("ef_target/gcam_kaist_ef_target_fill_audit.csv")
REVIEW_ID = "gcam_kaist_target_20260908"


@dataclass(frozen=True)
class Assignment:
    ef: str
    source_ids: tuple[str, ...]
    locator: str
    status: str
    production_ready: bool = False
    note: str = ""


CAPSS = ("capss_vii_2025",)

LIVESTOCK = {
    "Beef": (
        "NH3: cattle <1 y=11.8; 1-2 y=14.0; >2 y=16.8 kg/animal-year. "
        "PM2.5/TSP/PM10: beef cattle=0.16/0.72/0.24 kg/animal-year."
    ),
    "Dairy": (
        "NH3: dairy cow=24.6 kg/animal-year. PM2.5/TSP/PM10: 0.23/1.08/0.36 kg/animal-year."
    ),
    "Pork": (
        "NH3: piglet=4.40; growing=5.27; finishing=7.28; sow=21.40 kg/animal-year. "
        "PM2.5/TSP/PM10: piglet=0.029/0.54/0.18, grow-finish=0.069/1.26/0.42, "
        "sow=0.073/1.35/0.45 kg/animal-year."
    ),
    "Poultry": (
        "NH3: layer=0.37; broiler=0.061625; breeder=annual layer/broiler weighted mean "
        "kg/animal-year. "
        "PM2.5/TSP/PM10: layer=0.0021/0.05/0.017, "
        "broiler=0.000461/0.156/0.00294 kg/animal-year."
    ),
}

CROP_DUST = {
    "Rice": "Harvest PM2.5/TSP/PM10=0.28/4.14/1.88 kg/ha.",
    "Wheat": "Harvest PM2.5/TSP/PM10=0.97/14.31/6.50 kg/ha.",
    "RootTuber": "Harvest PM2.5/TSP/PM10=0.28/4.14/1.88 kg/ha.",
    "Corn": "Harvest PM2.5/TSP/PM10=0.28/4.14/1.88 kg/ha.",
    "Legumes": "Harvest PM2.5/TSP/PM10=0.28/4.14/1.88 kg/ha.",
    "OilCrop": "Harvest PM2.5/TSP/PM10=0.28/4.14/1.88 kg/ha.",
    "OtherGrain": "Harvest PM2.5/TSP/PM10=0.28/4.14/1.88 kg/ha.",
    "MiscCrop": "Harvest PM2.5/TSP/PM10=0.28/4.14/1.88 kg/ha.",
    "NutsSeeds": "Harvest PM2.5/TSP/PM10=0.28/4.14/1.88 kg/ha (other-crop class).",
    "Fruits": (
        "Harvest PM2.5/TSP/PM10=0.01/0.20/0.09 kg/ha for listed Korean orchard "
        "fruits; grapes=0.03/0.42/0.19 kg/ha."
    ),
    "Vegetables": (
        "Harvest PM2.5/TSP/PM10=0.01/0.20/0.09, 0.03/0.42/0.19, or "
        "0.28/4.14/1.88 kg/ha depending on crop in CAPSS Table 12-12."
    ),
}

CROP_BURN = {
    "Corn": "Residue burn PM2.5/NOx/VOC/CO/TSP/PM10/BC=0.00794/0.00900/0.04025/0.42739/0.02596/0.00971/0.0021 kg/kg residue; NH3 unavailable.",
    "Soybean": "Residue burn PM2.5/NOx/VOC/NH3/CO/TSP/PM10/BC=0.01011/0.00038/0.02736/0.00002/0.01584/0.03001/0.01197/0.0016 kg/kg residue.",
    "Wheat": "Barley/wheat residue proxy PM2.5/NOx/VOC/NH3/CO/TSP/PM10/BC=0.03524/0.01763/0.10520/0.00001/0.40344/0.08584/0.05307/0.0022 kg/kg residue.",
}

COAL_COMBUSTION = (
    "CAPSS bituminous-coal combustion PM2.5/SOx/NOx/VOC/NH3/CO/TSP/PM10="
    "10.1409/19S/5.55/0.03/0.00028/0.25/50/29.1 kg/ton fuel "
    "(manufacturing; S=fuel sulfur mass fraction in CAPSS convention); "
    "BC=PM2.5*0.018766."
)
GAS_COMBUSTION = (
    "CAPSS LNG combustion PM2.5/SOx/NOx/VOC/NH3/CO/TSP/PM10="
    "0.03/0.01/3.7/0.18/0.051/1.344/0.03/0.03 kg/10^3 m3 fuel; "
    "BC=PM2.5*0.384."
)
LIQUID_COMBUSTION = (
    "CAPSS B-C oil combustion PM2.5/SOx/NOx/VOC/NH3/CO/TSP/PM10="
    "(0.57715S+0.19066)/14.3S/6.64/0.13/0.10/0.60/(1.1S+0.39)/"
    "(0.80801S+0.27005) kg/kL fuel; retain S symbol until sulfur content is joined; "
    "B-C-oil BC=PM2.5*0.01."
)
WOOD_COMBUSTION = (
    "Korean wood boiler PM2.5/SOx/NOx/VOC/NH3/CO/TSP/PM10="
    "0.003647/0.000150/0.001417/0.047780/0.000013/0.146742/0.012192/0.005813 "
    "kg/kg wood; pellet boiler=0.002632/0.000183/0.011917/0.048750/0.000020/"
    "0.156973/0.004725/0.003405 kg/kg pellet; BC=0.00095 kg/kg wood-boiler fuel "
    "and 0.00031 kg/kg pellet-boiler fuel."
)
ROAD_FORMULA = (
    "CAPSS VII Appendix I tailpipe EF equations, g/vehicle-km, parameterized by "
    "pollutant, vehicle class, fuel, model year and speed V; calculate the annual "
    "factor by Korean fleet/speed weighting. PM10-to-PM2.5 and BC fractions must use "
    "the appendix's pollutant-specific rules."
)


def _conditional(ef: str, locator: str, note: str, *source_ids: str) -> Assignment:
    return Assignment(ef, source_ids or CAPSS, locator, "conditional_factor", False, note)


def _gap(note: str, locator: str = "Korean source search through 2026-09-08") -> Assignment:
    return Assignment(
        "GAP: no defensible Korea-specific criteria-pollutant EF located for this exact "
        "GCAM-KAIST process/technology; do not substitute zero.",
        CAPSS,
        locator,
        "research_gap",
        False,
        note,
    )


def _no_direct(note: str) -> Assignment:
    return Assignment(
        "NOT APPLICABLE: no direct on-site criteria-pollutant EF; upstream emissions "
        "belong to the supplying fuel/electricity sector.",
        CAPSS,
        "Direct-emissions boundary decision",
        "not_applicable",
        True,
        note,
    )


def _absent() -> Assignment:
    return Assignment(
        "NOT APPLICABLE TO CURRENT GCAM-KAIST: path is absent, so no EF is applied.",
        (),
        "GCAM-KAIST taxonomy reconciliation",
        "not_applicable",
        True,
        "Retained as an explicit reconciled target-table row; absence is not a zero EF.",
    )


def assignment_for(sector: str, subsector: str) -> Assignment:  # noqa: PLR0911, PLR0912
    """Return the evidence-backed assignment for one exact target-table row."""
    if sector.startswith("NOT FOUND IN GCAM-KAIST"):
        return _absent()

    if sector in LIVESTOCK:
        return _conditional(
            LIVESTOCK[sector],
            "CAPSS VII Tables 10-6 and 12-16",
            "GCAM livestock output must be converted to Korean animal counts and class shares.",
            "capss_vii_2025",
        )
    if sector == "SheepGoat":
        return _conditional(
            "NH3: sheep=0.46 and goat=0.46 kg/animal-year; no matching CAPSS livestock-dust "
            "factor is available.",
            "CAPSS VII Table 10-6",
            "GCAM livestock output must be converted to Korean sheep/goat counts.",
            "capss_vii_2025",
        )

    if sector in CROP_DUST:
        value = CROP_DUST[sector]
        if sector in CROP_BURN:
            value = f"{value} {CROP_BURN[sector]}"
        return _conditional(
            value,
            "CAPSS VII Tables 12-12 and 13-6",
            "Use cultivated/harvested area for dust and residue mass for burning; do not apply to crop mass.",
            "capss_vii_2025",
            "korean_crop_burning_2022",
        )
    if sector == "Soybean":
        return _conditional(
            "Harvest PM2.5/TSP/PM10=0.28/4.14/1.88 kg/ha. " + CROP_BURN[sector],
            "CAPSS VII Tables 12-12 and 13-6",
            "Two separate source boundaries: harvest dust per area and residue burning per residue mass.",
            "capss_vii_2025",
            "korean_crop_burning_2022",
        )
    if sector in {"FeedCrops", "FiberCrop", "FodderGrass", "FodderHerb_Residue"}:
        return _conditional(
            "Dry-field land preparation PM2.5/TSP/PM10=0.97/14.22/6.46 kg/ha.",
            "CAPSS VII Table 12-12",
            "Only the general land-preparation factor is supported; crop-specific harvest factor is unavailable.",
            "capss_vii_2025",
        )
    if sector in {"FoodDemand_NonStaples", "NonFoodDemand_Crops"}:
        return _no_direct(
            "Demand/accounting node; agricultural emissions remain with crop production."
        )

    if sector == "N fertilizer":
        return _conditional(
            "Manufacture, kg/ton product: nitric acid NOx=15.2; ammonia SOx/VOC/NH3/CO="
            "0.0288/4.72/2.1/7.9; ammonium nitrate PM2.5/NH3/TSP/PM10="
            "0.85018/36.57/2.151/1.09701; urea PM2.5/NH3/TSP/PM10="
            "0.07477/10.69/0.28/0.14532.",
            "CAPSS VII Table 4-14",
            "Corrects the former fertilizer-application mismatch; requires Korean product-mix weights.",
            "capss_vii_2025",
        )

    if sector == "UnmanagedLand" and subsector == "ForestFire_Korea":
        return Assignment(
            "PM2.5/NOx/VOC/CO/TSP/PM10/BC=98.1/40/242/1410/172/109/9.30856 "
            "kg/ha burned; SOx and NH3 unavailable. BC is PM2.5*0.0948885.",
            CAPSS,
            "CAPSS VII Table 11-5",
            "exact_factor",
            True,
            "Convert GCAM thousand km2 to burned hectares only when the activity is burned area.",
        )
    if sector == "UnmanagedLand":
        return _gap(
            "Forest-fire factors must not be transferred to deforestation or grassland fire."
        )
    if sector == "airCO2":
        return _no_direct("Carbon-flow accounting node, not a direct criteria-pollutant source.")
    if sector == "biomass":
        return _conditional(
            "Dry-field production dust PM2.5/TSP/PM10=0.97/14.22/6.46 kg/ha; "
            "combustion factors are not applied at the biomass-production boundary.",
            "CAPSS VII Table 12-12",
            "Requires harvested-area activity; excludes downstream combustion and open burning.",
            "capss_vii_2025",
        )

    if sector == "cement":
        return Assignment(
            "Clinker production PM2.5/TSP/PM10=0.01330/0.02020/0.01919 kg/ton clinker.",
            CAPSS,
            "CAPSS VII Table 4-31",
            "exact_factor",
            True,
            "Use only the clinker-mass activity; combustion is assigned to process-heat rows.",
        )

    if sector == "chemical energy use" and subsector == "coal":
        return _conditional(
            COAL_COMBUSTION,
            "CAPSS VII Table 3-3",
            "Convert EJ to tonnes of the matched coal grade.",
        )
    if sector == "chemical feedstocks":
        return _gap(
            "Feedstock carbon is not combustion; the earlier combustion-factor link was invalid."
        )

    if sector in {"comm cooling", "comm heating", "comm others"}:
        if subsector == "electricity":
            return _no_direct(
                "Purchased electricity; power-sector factors carry upstream emissions."
            )
        if subsector == "gas":
            return _conditional(
                GAS_COMBUSTION,
                "CAPSS VII Table 2-3",
                "Convert EJ to 10^3 m3 LNG; cooling technology remains a proxy.",
            )
        if subsector == "biomass":
            return _conditional(
                WOOD_COMBUSTION,
                "CAPSS VII Table 13-13",
                "Convert EJ to fuel mass and weight wood versus pellet.",
                "capss_vii_2025",
                "korean_wood_2015",
            )
        if subsector == "refined liquids":
            return _conditional(
                LIQUID_COMBUSTION,
                "CAPSS VII Table 2-3",
                "Convert EJ to kL and supply sulfur content.",
            )
        return _conditional(
            f"Fuel-specific set: {COAL_COMBUSTION} {GAS_COMBUSTION} {LIQUID_COMBUSTION}",
            "CAPSS VII Table 2-3",
            "Bundled end use requires GCAM fuel shares; no unweighted scalar is defensible.",
            "capss_vii_2025",
        )

    if sector == "elec_coal (conv pul)":
        return Assignment(
            "2022 Korean coal-fleet output factors NOx/SOx/TSP=0.10209/0.11022/0.008219 "
            "kg/MWh (ratio of sums across 14 complexes). 2017 official national factors: "
            "NOx/SOx/TSP/PM2.5=0.291/0.258/0.013/0.120 kg/MWh.",
            ("lee_2025_coal", "motie_2019_power", "yu_2021_coal"),
            "Lee 2025 Table 1; MOTIE 2019 national table; Yu 2021 Table 5",
            "exact_factor",
            True,
            "Use the same-year fleet factor when possible; values are controlled-stack/fleet evidence.",
        )
    if sector in {"elec_gas (CC)", "elec_gas (steam/CT)", "elec_gas (CC CCS)"}:
        note = "National gas-fleet factor is not technology-specific."
        if "CCS" in sector:
            note += " No Korean CCS-specific criteria-pollutant adjustment was located."
        return _conditional(
            "Official 2017 Korean gas-fleet NOx=0.171 and PM2.5=0.015 kg/MWh; "
            "SOx and TSP are unreported, not zero. CAPSS gas-turbine input set: "
            "PM2.5/SOx/NOx/VOC/NH3/CO/TSP/PM10=0.036/0.01/6.04/0.21/0.051/"
            "1.55/0.036/0.036 kg/10^3 m3 LNG.",
            "MOTIE 2019 national table; CAPSS VII Table 1-3",
            note,
            "motie_2019_power",
            "capss_vii_2025",
        )
    if sector == "elec_refined liquids (steam/CT)":
        return _conditional(
            "Korean oil-generation 2015-2017 ranges SOx=1.264-1.367, NOx=0.711-0.727, "
            "TSP=0.018-0.023, PM2.5=0.506-0.544 kg/MWh.",
            "Seo 2019 Tables 2-3",
            "Anonymized controlled oil unit; select year/technology explicitly.",
            "seo_2019_oil",
        )
    if sector == "elec_biomass (conv)":
        return _conditional(
            WOOD_COMBUSTION,
            "CAPSS VII Table 13-13; Korean wood combustion study",
            "Korean measured boiler factor, but plant-scale power boiler and fuel-mixture validation remain required.",
            "capss_vii_2025",
            "korean_wood_2015",
        )
    if sector == "elec_biomass (IGCC)":
        return _gap("No Korean biomass-IGCC criteria-pollutant factor was located.")
    if sector == "electricity":
        return _no_direct(
            "Accounting/intermediate electricity row; avoid double counting elec_* generation."
        )

    if sector == "H2 central production":
        if subsector in {"electricity", "nuclear"}:
            return _no_direct(
                "Electrolysis/nuclear heat boundary has no direct combustion EF in this table."
            )
        return _gap("No Korean technology-specific hydrogen-production criteria EF was located.")
    if sector in {"gas pipeline", "gas processing"}:
        return _gap(
            "CAPSS has related fuel-production categories but no denominator-compatible Korean factor for this GCAM process."
        )

    if sector == "industrial processes":
        if subsector == "nitric acid":
            return _conditional(
                "NOx=15.2 kg/ton nitric acid.",
                "CAPSS VII Table 4-14",
                "Target activity denominator is missing; join only to nitric-acid product mass.",
            )
        if subsector == "semiconductors":
            return _conditional(
                "VOC=39.463 kg/employee-year for electronic-component cleaning.",
                "CAPSS VII Table 6-17",
                "Employment factor is a CAPSS subcategory proxy, not a process-output factor.",
            )
        if subsector == "solvents":
            return _conditional(
                "Household/commercial solvent VOC=2.64 kg/person-year.",
                "CAPSS VII Table 6-23",
                "Generic GCAM process lacks population or solvent-use activity and must not absorb all solvent emissions.",
            )
        if subsector in {"HCFC_22_Prod", "adipic acid", "foams", "fire_exting"}:
            return _no_direct(
                "GCAM row is primarily a greenhouse-gas process; no direct criteria factor is assigned."
            )
        return _gap(
            "No exact Korean criteria-pollutant factor and denominator were located for this aggregate process."
        )

    if sector == "n/a (identified via technology)":
        return _gap(
            "Extraction technology is not identified at this row; retain fugitive/mining emissions as an explicit gap."
        )
    if sector.startswith("nuclearFuel"):
        return _no_direct(
            "Fuel-cycle activity has no direct Korean criteria EF at the modeled boundary."
        )

    if sector == "other industrial energy use":
        if subsector == "electricity":
            return _no_direct(
                "Purchased electricity; power-sector factors carry upstream emissions."
            )
        if subsector == "hydrogen":
            return _no_direct(
                "End-use hydrogen has no direct criteria emissions absent combustion technology evidence."
            )
        if subsector == "coal":
            return _conditional(
                COAL_COMBUSTION,
                "CAPSS VII Table 3-3",
                "Convert EJ to tonnes and weight controls/coal grades.",
            )
        if subsector == "gas":
            return _conditional(
                GAS_COMBUSTION, "CAPSS VII Table 3-3", "Convert EJ to 10^3 m3 LNG."
            )
        if subsector == "refined liquids":
            return _conditional(
                LIQUID_COMBUSTION,
                "CAPSS VII Table 3-3",
                "Convert EJ to kL and supply sulfur content.",
            )
        return _conditional(
            WOOD_COMBUSTION,
            "CAPSS VII Table 13-13",
            "Convert EJ to fuel mass and weight wood/pellet.",
            "capss_vii_2025",
            "korean_wood_2015",
        )
    if sector == "other industrial feedstocks":
        return _gap(
            "Feedstock use is not combustion; process-specific release fractions are required."
        )

    if sector == "process heat cement":
        factors = {
            "coal": COAL_COMBUSTION,
            "gas": GAS_COMBUSTION,
            "refined liquids": LIQUID_COMBUSTION,
            "biomass": WOOD_COMBUSTION,
        }
        if subsector == "hydrogen":
            return _gap("No Korean cement-kiln hydrogen criteria-pollutant EF was located.")
        sources = ("capss_vii_2025", "korean_wood_2015") if subsector == "biomass" else CAPSS
        return _conditional(
            factors[subsector],
            "CAPSS VII Tables 3-3 and 3-5",
            "Fuel-combustion proxy; convert EJ to the source denominator and apply kiln controls.",
            *sources,
        )
    if sector == "process heat dac":
        return _gap("No operating Korean gas-CCS DAC criteria-pollutant EF was located.")

    if sector == "refining":
        if subsector == "oil refining":
            return _conditional(
                "Petroleum processing PM2.5/SOx/NOx/NH3/CO/TSP/PM10="
                "0.001726/0.211435/0.030205/0.000949/0.035383/0.005178/0.004315 "
                "kg/kL feed; storage/handling VOC=0.09493 kg/kL.",
                "CAPSS VII Tables 4-4 and 5-2",
                "Convert GCAM EJ to refinery throughput; keep processing and storage boundaries separate.",
            )
        return _gap(
            "No Korean biomass-to-liquids, coal-to-liquids, or gas-to-liquids criteria EF was located."
        )

    if sector.startswith("regional "):
        return _no_direct(
            "Regional commodity-market accounting row; direct production, conversion, "
            "transport, and handling emissions stay with their physical process rows."
        )

    if sector in {"resid cooling", "resid heating", "resid others"}:
        if sector == "resid cooling":
            return _no_direct(
                "Modern residential cooling is electricity-only at the direct-emissions boundary."
            )
        if subsector == "TradBio":
            return _conditional(
                WOOD_COMBUSTION,
                "CAPSS VII Table 13-13",
                "Convert EJ to wood/pellet mass and weight appliance types.",
                "capss_vii_2025",
                "korean_wood_2015",
            )
        if subsector == "coal":
            return _conditional(
                COAL_COMBUSTION,
                "CAPSS VII Table 2-5",
                "Convert EJ to tonnes and match residential coal grade.",
            )
        return _conditional(
            f"Bundled fuel set: {WOOD_COMBUSTION} {GAS_COMBUSTION} {LIQUID_COMBUSTION}",
            "CAPSS VII Tables 2-5 and 13-13",
            "Modern/bundled end use requires fuel and appliance shares.",
            "capss_vii_2025",
            "korean_wood_2015",
        )

    if sector in {"trn_aviation_intl", "trn_pass"} and "Aviation" in subsector:
        return _conditional(
            "CAPSS 2022 landing/takeoff-cycle factors by 28 aircraft types: PM2.5/TSP/PM10="
            "0.0358-1.1656, SOx=0.6916-4.3697, NOx=5.6804-70.8692, "
            "VOC=0.0691-26.3762, CO=0.7127-91.7297 kg/LTO; NH3 unavailable.",
            "CAPSS VII Table 8-20",
            "Requires Korean aircraft-type LTO counts; GCAM passenger-km cannot directly multiply kg/LTO.",
        )
    if sector in {"trn_freight", "trn_shipping_intl"} and "Ship" in subsector:
        return _conditional(
            "Cargo ship, kg/ton fuel: diesel PM2.5/SOx/NOx/VOC/NH3/CO/TSP/PM10="
            "1.4/20S/78.5/2.8/0.007/7.4/1.5/1.5; heavy oil="
            "5.6/20S/79.3/2.7/0.007/7.4/6.2/6.2.",
            "CAPSS VII Table 8-12",
            "Requires fuel use, sulfur content, and fuel shares; ton-km is not the factor denominator.",
        )
    if (sector == "trn_freight" and subsector == "Freight Rail") or (
        sector == "trn_pass" and subsector == "Passenger Rail"
    ):
        return _conditional(
            "Diesel locomotive PM2.5/SOx/NOx/VOC/NH3/CO/TSP/PM10="
            "3.827/1.64/64.36/10.66/0.11/26.36/4.16/4.16 kg/kL diesel; "
            "electric traction has no direct EF.",
            "CAPSS VII Table 8-3",
            "Requires diesel consumption and diesel/electric traction shares.",
        )
    if sector == "trn_pass" and subsector in {"Cycle", "Walk", "HSR"}:
        return _no_direct(
            "Human-powered or electric traction; upstream electricity remains in power."
        )
    if sector.startswith("trn_"):
        return _conditional(
            ROAD_FORMULA,
            "CAPSS VII Appendix I (road mobile-source equations)",
            "GCAM passenger/ton-km requires occupancy/payload, fleet, speed, fuel and model-year weights.",
            "capss_vii_2025",
            "capss_nonexhaust_2025",
        )

    if sector == "urban processes":
        if subsector == "aerosols":
            return _conditional(
                "Household/commercial solvent VOC=2.64 kg/person-year.",
                "CAPSS VII Table 6-23",
                "Population factor is an aggregate proxy; isolate aerosol-product share before use.",
            )
        if subsector == "fire_exting":
            return _no_direct(
                "Fire-extinguishing-agent row is a greenhouse-gas process without a direct criteria EF."
            )
        if subsector == "waste_incineration":
            return Assignment(
                "Municipal waste PM2.5/SOx/NOx/VOC/CO/TSP/PM10="
                "0.03258/0.4/1.8/0.02/0.5/0.05/0.0362 kg/ton waste; NH3 unavailable.",
                CAPSS,
                "CAPSS VII Table 9-3",
                "exact_factor",
                False,
                "Target activity unit is missing; production use requires tonnes of incinerated waste.",
            )
        if subsector == "wastewater":
            return _conditional(
                "NH3: industrial wastewater=0.00381 and residential/commercial wastewater="
                "0.00217 g/ton wastewater (source-unit transcription retained).",
                "CAPSS VII Tables 9-7 and 9-8",
                "Confirm the handbook's g/ton unit and split wastewater type before use.",
            )
        if subsector == "landfills":
            return _conditional(
                "CAPSS landfill model: E_CH4=[MSWT*MSWF*MCF*DOC*DOCf*F*(16/12)-R]*(1-OX); "
                "defaults MCF=1, DOC=0.082, DOCf=0.77, F=0.5, R=0, OX=0. "
                "NMVOC uses landfill-gas flow and Cp=595 ppmv as hexane.",
                "CAPSS VII equations and Table 9-11",
                "Equation requires disposed waste history and landfill-gas activity; it is not a zero-order scalar.",
            )

    return _gap("No row-specific assignment rule matched; this is an implementation-visible gap.")


def _source_labels(source_ids: tuple[str, ...]) -> str:
    if not source_ids:
        return "GCAM-KAIST taxonomy reconciliation"
    source_path = REFERENCE_DIR / "gcam_kaist_ef_sources.csv"
    with source_path.open(encoding="utf-8", newline="") as handle:
        registry = {row["source_id"]: row["source_title"] for row in csv.DictReader(handle)}
    return " | ".join(registry[source_id] for source_id in source_ids)


def fill_target_table(
    target_path: Path, audit_path: Path, *, check_only: bool = False
) -> list[dict[str, str]]:
    """Populate column four and provenance, returning the row-level audit."""
    with target_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames
        rows = list(reader)
    if not fieldnames or "korea_specific_ef" not in fieldnames:
        raise ValueError(f"Target schema is missing korea_specific_ef: {target_path}")

    keys = [(row["gcam_kaist_sector"], row["gcam_kaist_subsector"]) for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("Target sector/subsector keys must be unique")

    audit: list[dict[str, str]] = []
    for row in rows:
        sector = row["gcam_kaist_sector"]
        subsector = row["gcam_kaist_subsector"]
        assignment = assignment_for(sector, subsector)
        row["korea_specific_ef"] = assignment.ef
        row["ef_source"] = _source_labels(assignment.source_ids)
        row["ef_link_note"] = assignment.note
        audit.append(
            {
                "gcam_kaist_sector": sector,
                "gcam_kaist_subsector": subsector,
                "status": assignment.status,
                "production_ready": str(assignment.production_ready).lower(),
                "source_ids": "|".join(assignment.source_ids),
                "source_locator": assignment.locator,
                "review_id": REVIEW_ID,
                "ef_text": assignment.ef,
                "note": assignment.note,
            }
        )

    if any(not row["ef_text"].strip() for row in audit):
        raise ValueError("Every target row must receive a factor, N/A decision, or explicit gap")
    if not check_only:
        with target_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        with audit_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(audit[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(audit)
    return audit


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, default=WORKSPACE_ROOT / TARGET_RELATIVE_PATH)
    parser.add_argument(
        "--audit",
        type=Path,
        default=RESULTS_DIAGNOSTICS_DIR / AUDIT_RELATIVE_PATH,
    )
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    audit = fill_target_table(args.target, args.audit, check_only=args.check_only)
    counts: dict[str, int] = {}
    for row in audit:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    print(f"Validated {len(audit)} target rows: {counts}")


if __name__ == "__main__":
    main()
