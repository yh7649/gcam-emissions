from __future__ import annotations

import csv
from pathlib import Path

from gcam_emissions.factors.kaist_target import assignment_for, fill_target_table


def _write_target(path: Path) -> None:
    fieldnames = [
        "gcam_kaist_sector",
        "gcam_kaist_subsector",
        "activity_unit",
        "korea_specific_ef",
        "capss_equivalent_sector",
        "capss_emission_value",
        "ef_source",
        "matched_via_gcam_usa_sector",
        "ef_link_note",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(
            {
                "gcam_kaist_sector": "cement",
                "gcam_kaist_subsector": "cement",
                "activity_unit": "Mt",
            }
        )
        writer.writerow(
            {
                "gcam_kaist_sector": "elec_biomass (IGCC)",
                "gcam_kaist_subsector": "biomass (IGCC)",
                "activity_unit": "EJ",
            }
        )


def test_assignments_preserve_values_and_gaps() -> None:
    cement = assignment_for("cement", "cement")
    assert "0.01330/0.02020/0.01919" in cement.ef
    assert cement.production_ready

    gap = assignment_for("elec_biomass (IGCC)", "biomass (IGCC)")
    assert gap.status == "research_gap"
    assert "do not substitute zero" in gap.ef


def test_fill_target_table_populates_every_row_and_audit(tmp_path: Path) -> None:
    target = tmp_path / "target.csv"
    audit = tmp_path / "audit.csv"
    _write_target(target)

    rows = fill_target_table(target, audit)

    assert len(rows) == 2
    assert all(row["ef_text"] for row in rows)
    assert audit.exists()
    with target.open(encoding="utf-8", newline="") as handle:
        populated = list(csv.DictReader(handle))
    assert all(row["korea_specific_ef"] for row in populated)
    assert populated[0]["ef_source"].startswith("National Air Pollutant")


def test_checked_in_target_has_135_explicit_assignments() -> None:
    target = Path(__file__).parents[1] / "docs/gcam_kaist_ef_target_table.csv"
    rows = fill_target_table(target, Path("unused.csv"), check_only=True)

    assert len(rows) == 135
    assert not any("implementation-visible gap" in row["note"] for row in rows)
    assert all(row["ef_text"] for row in rows)
