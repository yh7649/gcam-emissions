"""Compare GCAM-KAIST native non-CO2 emissions to CAPSS category totals.

Maps every GCAM-KAIST sector in gcam_kaist_nonco2_emissions_detail.csv onto one of
CAPSS's 13 first-level source categories via gcam_kaist_capss_category_crosswalk.csv,
sums emissions per category/pollutant/year/scenario, and compares against the CAPSS
"Emissions by Source Category" workbooks for 2015 and 2021.

Reads the detail table rather than the by-sector rollup because two CAPSS categories are
only separable below sector grain -- see the _AWB and solvents overrides in
load_gcam_by_category.

This is a screening/validation comparison, not a reconciliation: GCAM and CAPSS use
different sectoring logic (see the crosswalk's `note` column), GCAM reports no primary
PM2.5/PM10/TSP, and the Fugitive dust and Other surface-pollutant source categories have
no GCAM equivalent at all.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from gcam_emissions.config.paths import INTERIM_DIR, REFERENCE_DIR, RESULTS_DIAGNOSTICS_DIR

CROSSWALK_PATH = REFERENCE_DIR / "gcam_kaist_capss_category_crosswalk.csv"
DETAIL_PATH = (
    INTERIM_DIR / "gcam_native_emissions_by_sector" / "gcam_kaist_nonco2_emissions_detail.csv"
)
CAPSS_WORKBOOKS = {
    2015: Path("docs/2015%20Emissions%20by%20Source%20Category.xlsx"),
    2021: Path("docs/2021%20Emissions%20by%20Source%20Category.xlsx"),
}
CAPSS_POLLUTANT_COLUMNS = {
    "SOx": "SOx",
    "NOx": "NOx",
    "VOCs": "VOCs",
    "NH3": "NH3",
    "CO": "CO",
    "BC": "BC",
}
CAPSS_CATEGORIES = [
    "Energy production",
    "Non-industry",
    "Manufacturing industry",
    "Industrial process",
    "Energy transport and storage",
    "Solvent use",
    "Road transport",
    "Non-road transport",
    "Waste disposal",
    "Agriculture",
    "Other surface-pollutant source",
    "Fugitive dust",
    "Biomass burning",
]
EXCLUDED_CATEGORY = "excluded_international_bunker"


def load_capss_long(workbooks: dict[int, Path] = CAPSS_WORKBOOKS) -> pd.DataFrame:
    """Reshape the CAPSS "Emissions by Source Category" workbooks into a tidy table."""
    frames = []
    for year, path in workbooks.items():
        raw = pd.read_excel(path, sheet_name="Sheet1", header=1, index_col=0)
        raw = raw.loc[raw.index.notna() & (raw.index != "Total")]
        long = (
            raw[list(CAPSS_POLLUTANT_COLUMNS)]
            .reset_index(names="capss_category")
            .melt(id_vars="capss_category", var_name="pollutant", value_name="capss_tonnes")
        )
        long["year"] = year
        frames.append(long)
    combined = pd.concat(frames, ignore_index=True)
    combined["capss_tonnes"] = combined["capss_tonnes"].fillna(0.0)
    return combined


def load_gcam_by_category(
    detail_path: Path = DETAIL_PATH,
    crosswalk_path: Path = CROSSWALK_PATH,
) -> pd.DataFrame:
    """Apply the sector crosswalk (with the _AWB and solvents overrides) and sum by category."""
    detail = pd.read_csv(detail_path)
    detail = detail.loc[detail["mass_comparable"]]
    crosswalk = pd.read_csv(crosswalk_path)[["sector_type", "sector", "capss_category"]]

    merged = detail.merge(
        crosswalk, on=["sector_type", "sector"], how="left", validate="many_to_one"
    )
    if merged["capss_category"].isna().any():
        missing = sorted(merged.loc[merged["capss_category"].isna(), "sector"].unique())
        raise ValueError(f"Sectors missing from the CAPSS crosswalk: {missing}")

    # _AWB-tagged rows are open/residue burning regardless of which sector they're attached
    # to (e.g. Corn carries both fertilizer N2O_AGR -> Agriculture and residue-burning N2O_AWB
    # -> Biomass burning) -- this overrides the sector-level default for just those rows.
    is_awb = merged["native_pollutant"].str.endswith("_AWB")
    merged["capss_category"] = merged["capss_category"].where(~is_awb, "Biomass burning")

    # GCAM files solvent evaporation as a subsector of `industrial processes`, alongside genuine
    # process sources (adipic/nitric acid, HCFC-22, semiconductors, Al_Mg); CAPSS reports it as
    # its own first-level category. Mapping the sector whole-hog overstates Industrial process
    # VOCs ~4x and leaves Solvent use with no GCAM counterpart at all.
    is_solvents = (merged["sector"] == "industrial processes") & (
        merged["subsector"] == "solvents"
    )
    merged["capss_category"] = merged["capss_category"].where(~is_solvents, "Solvent use")

    merged = merged.loc[merged["capss_category"] != EXCLUDED_CATEGORY]

    grouped = merged.groupby(["scenario", "capss_category", "pollutant", "year"], as_index=False)[
        "emissions_kg"
    ].sum()
    grouped["gcam_tonnes"] = grouped["emissions_kg"] / 1000.0
    return grouped.drop(columns="emissions_kg")


SCENARIO_AGREEMENT_TOLERANCE = 0.01  # relative tolerance before scenarios are no longer "the same"


def build_comparison_table(years: tuple[int, ...] = (2015, 2021)) -> pd.DataFrame:
    """Build the comparison table, collapsing per-scenario GCAM columns into one gcam_kaist_tonnes.

    2015/2021 are historical years that both the nz and ref scenarios calibrate to identically,
    so scenario is not an informative axis here -- a single "GCAM-KAIST" series is reported. If
    years are ever added where the scenarios genuinely diverge, this raises rather than silently
    averaging away real differences.
    """
    capss = load_capss_long({y: CAPSS_WORKBOOKS[y] for y in years})
    gcam = load_gcam_by_category()
    gcam = gcam.loc[gcam["year"].isin(years) & gcam["pollutant"].isin(CAPSS_POLLUTANT_COLUMNS)]

    scaffold = pd.MultiIndex.from_product(
        [CAPSS_CATEGORIES, list(CAPSS_POLLUTANT_COLUMNS), years],
        names=["capss_category", "pollutant", "year"],
    ).to_frame(index=False)

    table = scaffold.merge(capss, on=["capss_category", "pollutant", "year"], how="left")
    table["capss_tonnes"] = table["capss_tonnes"].fillna(0.0)

    gcam_wide = gcam.pivot_table(
        index=["capss_category", "pollutant", "year"],
        columns="scenario",
        values="gcam_tonnes",
        fill_value=0.0,
    )
    spread = (gcam_wide.max(axis=1) - gcam_wide.min(axis=1)).abs()
    scale = gcam_wide.max(axis=1).clip(lower=1.0)
    disagreements = spread / scale > SCENARIO_AGREEMENT_TOLERANCE
    if disagreements.any():
        raise ValueError(
            "GCAM scenarios diverge by more than "
            f"{SCENARIO_AGREEMENT_TOLERANCE:.0%} for some category/pollutant/year combinations "
            "-- a single collapsed 'GCAM-KAIST' series would hide that. Report per-scenario "
            f"instead. Examples:\n{gcam_wide.loc[disagreements].head()}"
        )
    gcam_kaist = gcam_wide.mean(axis=1).rename("gcam_kaist_tonnes").reset_index()

    table = table.merge(gcam_kaist, on=["capss_category", "pollutant", "year"], how="left")
    table["gcam_kaist_tonnes"] = table["gcam_kaist_tonnes"].fillna(0.0)

    return table.sort_values(["year", "pollutant", "capss_category"]).reset_index(drop=True)


def plot_comparison(table: pd.DataFrame, *, year: int, output_path: Path) -> None:
    series = [("CAPSS", "capss_tonnes"), ("GCAM-KAIST", "gcam_kaist_tonnes")]
    pollutants = list(CAPSS_POLLUTANT_COLUMNS)
    year_table = table.loc[table["year"] == year]

    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    fig.suptitle(f"GCAM-KAIST vs CAPSS emissions by category, {year}", fontsize=14)
    bar_width = 0.8 / len(series)
    x = range(len(CAPSS_CATEGORIES))

    for ax, pollutant in zip(axes.flat, pollutants):
        sub = year_table.loc[year_table["pollutant"] == pollutant].set_index("capss_category")
        sub = sub.reindex(CAPSS_CATEGORIES)
        for i, (label, col) in enumerate(series):
            offset = (i - (len(series) - 1) / 2) * bar_width
            ax.bar([xi + offset for xi in x], sub[col] / 1000.0, width=bar_width, label=label)
        ax.set_title(pollutant)
        ax.set_ylabel("Emissions (kt/yr)")
        ax.set_xticks(list(x))
        ax.set_xticklabels(CAPSS_CATEGORIES, rotation=90, fontsize=7)

    axes.flat[0].legend(loc="upper right", fontsize=8)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--years", nargs="+", type=int, default=[2015, 2021])
    parser.add_argument(
        "--output-dir", type=Path, default=RESULTS_DIAGNOSTICS_DIR / "capss_comparison"
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    table = build_comparison_table(tuple(args.years))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    table_path = args.output_dir / "gcam_capss_category_comparison.csv"
    table.to_csv(table_path, index=False)
    print(f"wrote {table_path}")
    for year in args.years:
        chart_path = args.output_dir / f"gcam_capss_category_comparison_{year}.png"
        plot_comparison(table, year=year, output_path=chart_path)
        print(f"wrote {chart_path}")


if __name__ == "__main__":
    main()
