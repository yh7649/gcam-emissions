"""Run the BaseX non-CO2-by-sector query against GCAM-KAIST scenario databases.

Companion to xml_extract.py: that module streams a flat XML/zip archive, but the
GCAM-KAIST scenario output here ships pre-indexed as BaseX databases (see
queries/nonco2_emissions_by_sector.xq for setup). This shells out to the `basex`
CLI per scenario database, then normalizes the combined result the same way
xml_extract.py does (pollutant aliasing, unit-to-kg conversion) into tidy tables.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from io import StringIO
import json
from pathlib import Path
import subprocess

import pandas as pd

from gcam_emissions.config.paths import INTERIM_DIR
from gcam_emissions.gcam.xml_extract import POLLUTANT_ALIASES, _emissions_to_kg

QUERY_PATH = Path(__file__).resolve().parent / "queries" / "nonco2_emissions_by_sector.xq"
DEFAULT_SCENARIOS = ("nz", "ref")
DEFAULT_REGION = "South Korea"
DETAIL_COLUMNS = [
    "scenario",
    "region",
    "sector_type",
    "sector",
    "subsector_type",
    "subsector",
    "technology_type",
    "technology",
    "native_pollutant",
    "year",
    "native_emissions",
    "native_emissions_unit",
]


class BaseXQueryError(RuntimeError):
    """Raised when the `basex` CLI is missing or a scenario query fails."""


def _run_basex_query(
    scenario_db: str, *, region: str, years: tuple[int, ...] = ()
) -> pd.DataFrame:
    years_arg = ",".join(str(year) for year in years)
    try:
        result = subprocess.run(
            [
                "basex",
                "-b",
                f"scenario-label={scenario_db}",
                "-b",
                f"region-name={region}",
                "-b",
                f"years={years_arg}",
                str(QUERY_PATH),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as error:
        raise BaseXQueryError(
            "The `basex` CLI is not on PATH. Install it (e.g. `brew install basex`) and "
            "register the scenario database in BaseX's DBPATH first."
        ) from error
    if result.returncode != 0:
        raise BaseXQueryError(
            f"basex query against database {scenario_db!r} failed:\n{result.stderr}"
        )
    return pd.read_csv(StringIO(result.stdout), dtype={"year": int}, keep_default_na=False)


def build_nonco2_by_sector_tables(
    *,
    scenario_dbs: tuple[str, ...] = DEFAULT_SCENARIOS,
    region: str = DEFAULT_REGION,
    years: tuple[int, ...] = (),
    output_dir: Path = INTERIM_DIR / "gcam_native_emissions_by_sector",
) -> dict[str, object]:
    """Query every registered scenario database and emit detail + by-sector tables."""
    frames = [_run_basex_query(db, region=region, years=years) for db in scenario_dbs]
    detail = pd.concat(frames, ignore_index=True)[DETAIL_COLUMNS]

    detail["pollutant"] = detail["native_pollutant"].map(lambda p: POLLUTANT_ALIASES.get(p, p))
    detail["emissions_kg"] = [
        _emissions_to_kg(value, unit)
        for value, unit in zip(detail["native_emissions"], detail["native_emissions_unit"])
    ]
    detail["mass_comparable"] = detail["emissions_kg"].notna()
    detail = detail.sort_values(
        [
            "scenario",
            "year",
            "sector_type",
            "sector",
            "subsector",
            "technology",
            "native_pollutant",
        ],
        kind="stable",
    ).reset_index(drop=True)

    by_sector = (
        detail.loc[detail["mass_comparable"]]
        .groupby(
            ["scenario", "sector_type", "sector", "pollutant", "native_pollutant", "year"],
            as_index=False,
        )
        .agg(emissions_kg=("emissions_kg", "sum"), source_row_count=("emissions_kg", "size"))
        .sort_values(["scenario", "sector", "pollutant", "year"])
        .reset_index(drop=True)
    )
    by_sector["emissions_kt"] = by_sector["emissions_kg"] / 1_000_000.0

    # CO2_FUG (fugitive CO2 tracked under the Non-CO2 tag) is reported in MTC, a carbon-mass
    # quantity that is not comparable to the species-mass units the kg/kt sums above use.
    non_mass = (
        detail.loc[~detail["mass_comparable"]]
        .groupby(
            [
                "scenario",
                "sector_type",
                "sector",
                "native_pollutant",
                "native_emissions_unit",
                "year",
            ],
            as_index=False,
            dropna=False,
        )
        .agg(native_emissions=("native_emissions", "sum"))
        .sort_values(["scenario", "sector", "native_pollutant", "year"])
        .reset_index(drop=True)
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    suffix = "_" + "-".join(str(year) for year in sorted(years)) if years else ""
    paths = {
        "detail": output_dir / f"gcam_kaist_nonco2_emissions_detail{suffix}.csv",
        "by_sector": output_dir / f"gcam_kaist_nonco2_emissions_by_sector{suffix}.csv",
        "non_mass_comparable": output_dir / f"gcam_kaist_non_mass_comparable_species{suffix}.csv",
        "metadata": output_dir / f"gcam_kaist_nonco2_by_sector{suffix}.metadata.json",
    }
    detail.to_csv(paths["detail"], index=False)
    by_sector.to_csv(paths["by_sector"], index=False)
    non_mass.to_csv(paths["non_mass_comparable"], index=False)

    metadata: dict[str, object] = {
        "dataset": "GCAM-KAIST native non-CO2 emissions by sector (all sectors)",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "scenario_databases": list(scenario_dbs),
        "region": region,
        "years": sorted(years) if years else "all",
        "detail_rows": int(len(detail)),
        "by_sector_rows": int(len(by_sector)),
        "non_mass_comparable_rows": int(len(non_mass)),
        "distinct_sectors": sorted(detail["sector"].unique()),
        "distinct_pollutants": sorted(detail["pollutant"].unique()),
        "analytical_use_permitted": False,
        "limitations": [
            "Native GCAM emissions are a validation lane, not approved Korean activity-times-EF emissions.",
            "sector_type='resource' rows are fugitive emissions from resource extraction "
            "(e.g. coal-mining CH4), not supplysector output.",
            "CO2_FUG rows use MTC (carbon mass) and are excluded from the by-sector kg/kt sums; "
            "see the non_mass_comparable table.",
        ],
        "outputs": {key: path.name for key, path in paths.items() if key != "metadata"},
    }
    paths["metadata"].write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return metadata


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario-dbs", nargs="+", default=list(DEFAULT_SCENARIOS))
    parser.add_argument("--region", default=DEFAULT_REGION)
    parser.add_argument("--years", nargs="+", type=int, default=[])
    parser.add_argument(
        "--output-dir", type=Path, default=INTERIM_DIR / "gcam_native_emissions_by_sector"
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    result = build_nonco2_by_sector_tables(
        scenario_dbs=tuple(args.scenario_dbs),
        region=args.region,
        years=tuple(args.years),
        output_dir=args.output_dir,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
