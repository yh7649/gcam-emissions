"""Regenerate every figure and data table used in docs/gcam_nonco2_investigation.md.

Each figure is written as a PNG next to this script, and the exact numbers it plots are written to
docs/figures/data/<figure>.csv (the table view). Inputs are local diagnostics produced during the
investigation; they live under the workspace root (GCAM_EMISSIONS_HOME, default: the current
directory) and are not tracked:

  results/diagnostics/capss_calibration_test/capss_mapping_search_{default,best}.csv
  results/diagnostics/nonco2_coverage/{implied_ef_long,driver_consistent_coef}.csv
  results/diagnostics/policy_experiment/{policy_experiment_summary,drv_ref}.csv
  data/interim/gcam_native_emissions_by_sector/gcam_kaist_nonco2_emissions_detail.csv

Run from the repo root:  .venv/bin/python docs/figures/make_figures.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from gcam_emissions.config.paths import INTERIM_DIR, RESULTS_DIAGNOSTICS_DIR  # noqa: E402

FIG_DIR = Path(__file__).resolve().parent
DATA_DIR = FIG_DIR / "data"
# The paper folder must stand alone (e.g. on Overleaf), so it keeps its own copy of each PNG.
PAPER_FIG_DIR = FIG_DIR.parents[1] / "paper" / "Figures"
CAPSS_TEST = RESULTS_DIAGNOSTICS_DIR / "capss_calibration_test"
COVERAGE = RESULTS_DIAGNOSTICS_DIR / "nonco2_coverage"
POLICY = RESULTS_DIAGNOSTICS_DIR / "policy_experiment"
DETAIL = INTERIM_DIR / "gcam_native_emissions_by_sector" / "gcam_kaist_nonco2_emissions_detail.csv"

# Reference palette (light mode), validated: slots 1-3 pass all-pairs CVD and normal-vision checks.
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
GRID, AXIS, WASH = "#e1e0d9", "#c3c2b7", "#f0efec"
MWH_PER_EJ_FACTOR = 3.6  # Tg per EJ of electricity -> kg per MWh

CAPSS_ORDER = [
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
POLLUTANTS = ["SOx", "NOx", "VOCs", "NH3", "CO", "BC"]

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.titleweight": "semibold",
        "axes.titlecolor": INK,
        "axes.labelcolor": INK2,
        "axes.edgecolor": AXIS,
        "axes.linewidth": 0.8,
        "axes.facecolor": SURFACE,
        "figure.facecolor": SURFACE,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "xtick.labelcolor": INK2,
        "ytick.labelcolor": INK2,
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "grid.linestyle": "-",
        "legend.frameon": False,
        "legend.labelcolor": INK2,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
    }
)


def _style(ax, grid_axis="x"):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(axis=grid_axis)
    ax.set_axisbelow(True)


def _save(fig, name: str, data: pd.DataFrame) -> None:
    fig.savefig(FIG_DIR / f"{name}.png")
    if PAPER_FIG_DIR.is_dir():
        fig.savefig(PAPER_FIG_DIR / f"{name}.png")
    plt.close(fig)
    data.to_csv(DATA_DIR / f"{name}.csv", index=False)
    print(f"wrote {name}.png and data/{name}.csv")


# --------------------------------------------------------------------------- fig 1
def capss_vs_gcam(year: int) -> None:
    t = pd.read_csv(CAPSS_TEST / "capss_mapping_search_default.csv")
    t = t[(t.year == year) & t.pollutant.isin(POLLUTANTS)]
    fig, axes = plt.subplots(2, 3, figsize=(10.5, 7.2), sharey=True)
    y = np.arange(len(CAPSS_ORDER))
    h = 0.34
    for ax, pol in zip(axes.flat, POLLUTANTS):
        s = t[t.pollutant == pol].set_index("capss_category").reindex(CAPSS_ORDER).fillna(0)
        ax.barh(y - h / 2 - 0.02, s.capss_t / 1000, height=h, color=BLUE, label="CAPSS")
        ax.barh(y + h / 2 + 0.02, s.gcam_t / 1000, height=h, color=ORANGE, label="GCAM-KAIST")
        ax.set_title(pol, loc="left")
        ax.set_yticks(y, CAPSS_ORDER)
        ax.invert_yaxis()
        ax.set_xlabel("kt per year")
        _style(ax)
    axes.flat[0].legend(loc="lower right", fontsize=8)
    fig.suptitle(
        f"CAPSS vs GCAM-KAIST by CAPSS source category, {year}",
        x=0.01,
        ha="left",
        fontsize=11,
        fontweight="semibold",
        color=INK,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    data = t[["year", "capss_category", "pollutant", "capss_t", "gcam_t", "ratio"]]
    _save(fig, f"fig01_capss_vs_gcam_{year}", data)


# --------------------------------------------------------------------------- fig 2
def agreement_strip() -> None:
    t = pd.read_csv(CAPSS_TEST / "capss_mapping_search_default.csv")
    t = t[(t.capss_t > 0) & (t.gcam_t > 0)].copy()
    t["abs_rel_diff_pct"] = (t.gcam_t / t.capss_t - 1).abs() * 100
    t["near_exact"] = t.abs_rel_diff_pct < 0.12
    order = ["NH3", "SOx", "NOx", "VOCs", "CO", "BC"]
    fig, ax = plt.subplots(figsize=(8, 3.4))
    rng = np.random.default_rng(0)
    for i, pol in enumerate(order):
        s = t[t.pollutant == pol]
        jitter = rng.uniform(-0.18, 0.18, len(s))
        x = s.abs_rel_diff_pct.clip(lower=0.001)
        ax.scatter(
            x[~s.near_exact],
            i + jitter[~s.near_exact.to_numpy()],
            s=26,
            color=AXIS,
            edgecolor=SURFACE,
            linewidth=1,
            zorder=2,
            label="other cells" if i == 0 else None,
        )
        ax.scatter(
            x[s.near_exact],
            i + jitter[s.near_exact.to_numpy()],
            s=34,
            color=BLUE,
            edgecolor=SURFACE,
            linewidth=1,
            zorder=3,
            label="within 0.12% of CAPSS" if i == 0 else None,
        )
    ax.set_xscale("log")
    ax.set_yticks(range(len(order)), order)
    ax.invert_yaxis()
    ax.axvline(0.12, color=MUTED, linewidth=0.8, zorder=1)
    ax.set_xlabel(
        "|GCAM-KAIST / CAPSS − 1|, % (log scale; differences below 0.001% drawn at 0.001%)"
    )
    ax.set_xticks([0.01, 0.1, 1, 10, 100, 1000], ["0.01", "0.1", "1", "10", "100", "1,000"])
    n_exact = int(t.near_exact.sum())
    ax.set_title(
        f"Agreement with CAPSS: {n_exact} of {len(t)} category × pollutant × year cells "
        "within 0.12%",
        loc="left",
        pad=22,
    )
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, fontsize=8, borderaxespad=0.2)
    ax.set_xlim(0.0006, None)
    _style(ax)

    data = t[
        [
            "year",
            "capss_category",
            "pollutant",
            "capss_t",
            "gcam_t",
            "abs_rel_diff_pct",
            "near_exact",
        ]
    ].sort_values("abs_rel_diff_pct")
    _save(fig, "fig02_capss_agreement", data)


# --------------------------------------------------------------------------- mapping table
def mapping_search_table() -> None:
    rows = []
    for name in ("default", "best"):
        t = pd.read_csv(CAPSS_TEST / f"capss_mapping_search_{name}.csv")
        nat = t.groupby(["year", "pollutant"]).capss_t.transform("sum")
        score = ((t.gcam_t - t.capss_t).abs() / nat).groupby([t.year, t.pollutant]).sum().mean()
        both = t[(t.capss_t > 0) & (t.gcam_t > 0)]
        rel = (both.gcam_t / both.capss_t - 1).abs()
        rows.append(
            {
                "mapping": name,
                "misallocated_share_of_capss_mass": round(score, 4),
                "cells_with_both_positive": len(both),
                "within_0.12pct": int((rel < 0.0012).sum()),
                "within_1pct": int((rel < 0.01).sum()),
                "within_5pct": int((rel < 0.05).sum()),
                "within_10pct": int((rel < 0.10).sum()),
            }
        )
    pd.DataFrame(rows).to_csv(DATA_DIR / "table_mapping_search.csv", index=False)
    print("wrote data/table_mapping_search.csv")


# --------------------------------------------------------------------------- fig 3
def gas_cc_vs_steamct() -> None:
    e = pd.read_csv(COVERAGE / "implied_ef_long.csv")
    e = e[
        (e.scenario == "ref")
        & (e.sector == "electricity")
        & (e.subsector == "gas")
        & e.pollutant.isin(["NOx", "CO"])
    ]
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.4))
    for ax, pol in zip(axes, ["NOx", "CO"]):
        s = e[e.pollutant == pol].pivot_table(
            index="year", columns="technology", values="ef_kg_per_TJ"
        )
        ax.axvspan(2004, 2021.5, color=WASH, zorder=0)
        ax.plot(
            s.index,
            s["gas (CC)"],
            color=BLUE,
            linewidth=1.6,
            marker="o",
            markersize=5,
            markeredgecolor=SURFACE,
            label="gas (CC), combined cycle",
            zorder=3,
        )
        ax.plot(
            s.index,
            s["gas (steam/CT)"],
            color=ORANGE,
            linewidth=0,
            marker="o",
            markersize=8,
            markerfacecolor="none",
            markeredgewidth=1.6,
            label="gas (steam/CT)",
            zorder=4,
        )
        ax.set_title(f"{pol}, kg per TJ of gas burned", loc="left")
        ax.set_xticks(s.index)
        ax.set_ylim(0, s.to_numpy().max() * 1.12)
        _style(ax, "y")
    axes[0].text(
        2012.8,
        axes[0].get_ylim()[1] * 0.97,
        "base years",
        color=MUTED,
        fontsize=8,
        ha="center",
        va="top",
    )
    axes[0].legend(loc="upper right", fontsize=8)
    fig.suptitle(
        "Gas power: one factor for two technologies in every base year",
        x=0.01,
        ha="left",
        fontsize=11,
        fontweight="semibold",
        color=INK,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    data = e[["year", "technology", "pollutant", "ef_kg_per_TJ", "fuel_EJ", "emissions_kg"]]
    _save(fig, "fig03_gas_cc_vs_steamct", data.sort_values(["pollutant", "technology", "year"]))


# --------------------------------------------------------------------------- fig 4
def mobile_vs_stationary() -> None:
    d = pd.read_csv(DETAIL)
    d = d[
        (d.scenario == "ref")
        & (d.technology == "refined liquids")
        & (d.native_pollutant == "NOx")
        & d.sector.isin(["agricultural energy use", "construction energy use"])
        & d.year.isin([2005, 2010, 2015, 2021])
    ]
    d = d.groupby(["sector", "subsector", "year"], as_index=False).native_emissions.sum()
    d["NOx_kt"] = d.native_emissions * 1000
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.2))
    for ax, sec in zip(axes, ["agricultural energy use", "construction energy use"]):
        s = d[d.sector == sec].pivot_table(index="year", columns="subsector", values="NOx_kt")
        x = np.arange(len(s))
        w = 0.3
        ax.bar(x - w / 2 - 0.02, s["mobile"], width=w, color=BLUE, label="mobile")
        ax.bar(x + w / 2 + 0.02, s["stationary"], width=w, color=ORANGE, label="stationary")
        ax.set_xticks(x, s.index)
        ax.set_ylabel("NOx, kt")
        ax.set_title(f"{sec}, refined liquids", loc="left")
        _style(ax, "y")
    axes[0].legend(loc="upper right", fontsize=8)
    fig.suptitle(
        "Mobile and stationary machinery carry identical emission masses",
        x=0.01,
        ha="left",
        fontsize=11,
        fontweight="semibold",
        color=INK,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    _save(fig, "fig04_mobile_vs_stationary", d[["sector", "subsector", "year", "NOx_kt"]])


# --------------------------------------------------------------------------- fig 5
TRAJ = [
    ("electricity", "coal", "coal (conv pul)", "NOx", MWH_PER_EJ_FACTOR, "Coal power NOx, kg/MWh"),
    ("trn_pass_road_LDV_4W", "Car", "Liquids", "NOx", 1.0, "Car (petrol/diesel) NOx, kg/GJ fuel"),
    ("process heat cement", "coal", "coal", "NOx", 1.0, "Cement-kiln coal NOx, kg/GJ coal"),
    ("comm others", "gas", "gas", "NOx", 1.0, "Commercial gas NOx, kg/GJ gas"),
]


def coefficient_trajectories() -> None:
    x = pd.read_csv(COVERAGE / "driver_consistent_coef.csv")
    fig, axes = plt.subplots(2, 2, figsize=(9, 6))
    rows = []
    for ax, (sec, sub, tech, pol, mult, title) in zip(axes.flat, TRAJ):
        q = x[
            (x.sector == sec)
            & (x.subsector == sub)
            & (x.technology == tech)
            & (x.native_pollutant == pol)
        ]
        p = q.pivot_table(index="year", columns="scenario", values="coef_native_units") * mult
        ax.axvspan(2004, 2021.5, color=WASH, zorder=0)
        ax.plot(
            p.index,
            p["ref"],
            color=BLUE,
            linewidth=1.6,
            marker="o",
            markersize=5,
            markeredgecolor=SURFACE,
            label="ref",
            zorder=3,
        )
        ax.plot(
            p.index,
            p["nz"],
            color=ORANGE,
            linewidth=0,
            marker="o",
            markersize=8,
            markerfacecolor="none",
            markeredgewidth=1.6,
            label="nz",
            zorder=4,
        )
        ax.set_title(title, loc="left")
        ax.set_xticks(p.index)
        ax.set_ylim(0, p.to_numpy().max() * 1.12)
        _style(ax, "y")
        for yr, r in p.iterrows():
            rows.append({"series": title, "year": yr, "ref": r["ref"], "nz": r["nz"]})
    axes.flat[0].text(
        2012.8,
        axes.flat[0].get_ylim()[1] * 0.97,
        "base years",
        color=MUTED,
        fontsize=8,
        ha="center",
        va="top",
    )
    axes.flat[0].legend(loc="upper right", fontsize=8)
    fig.suptitle(
        "Implied coefficients: unstable in base years, then frozen or declining identically "
        "in both scenarios",
        x=0.01,
        ha="left",
        fontsize=11,
        fontweight="semibold",
        color=INK,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    _save(fig, "fig07_coefficient_trajectories", pd.DataFrame(rows))


# --------------------------------------------------------------------------- fig 6
def base_year_swing() -> None:
    x = pd.read_csv(COVERAGE / "driver_consistent_coef.csv")
    w = x[x.scenario == "ref"].pivot_table(
        index=["sector", "subsector", "technology", "native_pollutant"],
        columns="year",
        values="coef_native_units",
    )
    cal = w[[2005, 2010, 2015, 2021]].dropna()
    cal = cal[(cal > 0).all(axis=1)]
    ratio = (cal.max(axis=1) / cal.min(axis=1)).rename("max_over_min")
    fig, ax = plt.subplots(figsize=(8, 3.4))
    bins = np.logspace(0, np.log10(ratio.max() * 1.05), 28)
    ax.hist(ratio, bins=bins, color=BLUE, edgecolor=SURFACE, linewidth=1)
    ax.set_xscale("log")
    med = ratio.median()
    ax.axvline(med, color=INK2, linewidth=0.8)
    ax.text(med * 1.06, ax.get_ylim()[1] * 0.92, f"median {med:.2f}×", color=INK2, fontsize=8)
    ax.set_xticks([1, 2, 5, 10, 20, 50, 100], ["1×", "2×", "5×", "10×", "20×", "50×", "100×"])
    ax.set_xlabel("largest ÷ smallest implied coefficient across 2005, 2010, 2015, 2021")
    ax.set_ylabel("technology-pollutant series")
    ax.set_title(
        f"How much base-year coefficients swing (n = {len(ratio)}; "
        f"{(ratio > 2).mean():.0%} swing more than 2×)",
        loc="left",
    )
    _style(ax, "y")
    _save(fig, "fig05_base_year_swing", ratio.reset_index())


# --------------------------------------------------------------------------- fig 7
def placeholder_shares() -> None:
    drv = pd.read_csv(POLICY / "drv_ref.csv")
    misc = drv[(drv.flow == "input") & (drv.flow_name == "misc emissions sources")][
        ["sector", "subsector", "technology"]
    ].drop_duplicates()
    d = pd.read_csv(DETAIL)
    d = d[
        (d.scenario == "ref")
        & (d.year == 2021)
        & d.mass_comparable
        & d.pollutant.isin(["NOx", "SOx", "VOCs", "NH3", "CO", "BC", "OC"])
        & ~d.sector.isin(["trn_aviation_intl", "trn_shipping_intl"])
    ]
    key = d.set_index(["sector", "subsector", "technology"]).index
    d["placeholder"] = key.isin(misc.set_index(["sector", "subsector", "technology"]).index)
    g = d.groupby(["pollutant", "placeholder"]).emissions_kg.sum().unstack(fill_value=0)
    out = pd.DataFrame({"placeholder_kt": g[True] / 1e6, "total_kt": g.sum(axis=1) / 1e6})
    out["share"] = out.placeholder_kt / out.total_kt
    out = out.sort_values("share", ascending=False).reset_index()
    fig, ax = plt.subplots(figsize=(7.5, 3.2))
    y = np.arange(len(out))
    ax.barh(y, out.share * 100, height=0.42, color=BLUE)
    for yi, r in out.iterrows():
        part = f"{r.placeholder_kt:,.1f}" if r.placeholder_kt < 10 else f"{r.placeholder_kt:,.0f}"
        ax.text(
            r.share * 100 + 1,
            yi,
            f"{r.share:.0%}  ({part} of {r.total_kt:,.0f} kt)",
            va="center",
            color=INK2,
            fontsize=8,
        )
    ax.set_yticks(y, out.pollutant)
    ax.invert_yaxis()
    ax.set_xlim(0, 115)
    ax.set_xticks([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"])
    ax.set_title(
        "Share of 2021 GCAM-KAIST emissions on placeholder-driven tags (ref, excl. intl. "
        "shipping and aviation)",
        loc="left",
    )
    _style(ax)
    _save(fig, "fig06_placeholder_shares", out)


# --------------------------------------------------------------------------- figs 8-10
VARIANT_LABELS = {
    "native": "GCAM-KAIST native",
    "gcam_2021": "GCAM's 2021 factors, held fixed",
    "korea_fleet": "Korean fleet factors",
    "korea_2017": "Korean 2017 official factors",
    "filled_low": "Untagged routes filled (CAPSS EAF factor)",
    "filled": "Hybrids filled (conventional factor)",
}


def policy_power() -> None:
    s = pd.read_csv(POLICY / "policy_experiment_summary.csv")
    s = s[(s.leg == "power") & s.pollutant.isin(["NOx", "SOx"])].copy()
    order = ["native", "gcam_2021", "korea_fleet", "korea_2017"]
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.2), sharey=True)
    for ax, pol in zip(axes, ["NOx", "SOx"]):
        p = s[s.pollutant == pol].set_index("variant").reindex(order)
        y = np.arange(len(order))
        colors = [MUTED] + [BLUE] * 3
        ax.barh(y, p.reduction_kt, height=0.42, color=colors)
        for yi, (v, r) in enumerate(p.iterrows()):
            label = f"{r.reduction_kt:.1f} kt" + (
                "" if v == "native" else f"  ({r.reduction_vs_native:.1f}×)"
            )
            ax.text(
                r.reduction_kt + p.reduction_kt.max() * 0.02,
                yi,
                label,
                va="center",
                color=INK2,
                fontsize=8,
            )
        ax.set_yticks(y, [VARIANT_LABELS[v] for v in order])
        ax.invert_yaxis()
        ax.set_xlim(0, p.reduction_kt.max() * 1.35)
        ax.set_xlabel("kt avoided in 2050 (ref − nz)")
        ax.set_title(f"{pol} avoided by nz, power sector", loc="left")
        _style(ax)
    fig.suptitle(
        "Power: same direction, but the avoided emissions vary 2.6–9.7× with the factors",
        x=0.01,
        ha="left",
        fontsize=11,
        fontweight="semibold",
        color=INK,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    _save(fig, "fig08_policy_power", s.sort_values(["pollutant", "variant"]))


def policy_steel() -> None:
    s = pd.read_csv(POLICY / "policy_experiment_summary.csv")
    s = s[
        (s.leg == "steel")
        & s.variant.isin(["native", "filled_low"])
        & s.pollutant.isin(["NOx", "SOx", "VOCs"])
    ].copy()
    s["change_pct"] = -s.reduction_pct  # nz relative to ref
    pols = ["NOx", "SOx", "VOCs"]
    fig, ax = plt.subplots(figsize=(8, 3.2))
    y = np.arange(len(pols))
    h = 0.3
    for off, v, c in ((-h / 2 - 0.02, "native", BLUE), (h / 2 + 0.02, "filled_low", ORANGE)):
        p = s[s.variant == v].set_index("pollutant").reindex(pols)
        ax.barh(y + off, p.change_pct, height=h, color=c, label=VARIANT_LABELS[v])
        for yi, val in enumerate(p.change_pct):
            ax.text(
                val + (2 if val >= 0 else -2),
                yi + off,
                f"{val:+.0f}%",
                va="center",
                ha="left" if val >= 0 else "right",
                color=INK2,
                fontsize=8,
            )
    ax.axvline(0, color=AXIS, linewidth=0.8)
    ax.set_yticks(y, pols)
    ax.invert_yaxis()
    ax.set_xlim(-110, 50)
    ax.set_xlabel("change in steel-sector emissions, nz vs ref, 2050 (%)")
    ax.set_title("Steel: filling the untagged routes flips the sign for SOx and VOCs", loc="left")
    ax.legend(loc="lower left", fontsize=8)
    _style(ax)
    _save(fig, "fig09_policy_steel", s[["pollutant", "variant", "ref", "nz", "change_pct"]])


def policy_road() -> None:
    s = pd.read_csv(POLICY / "policy_experiment_summary.csv")
    s = s[(s.leg == "road") & s.pollutant.isin(["NOx", "CO", "VOCs"])].copy()
    pols = ["NOx", "CO", "VOCs"]
    fig, axes = plt.subplots(1, 3, figsize=(10, 3.2))
    for ax, pol in zip(axes, pols):
        p = s[s.pollutant == pol].set_index("variant")
        x = np.arange(2)
        w = 0.3
        for off, v, c in ((-w / 2 - 0.02, "native", BLUE), (w / 2 + 0.02, "filled", ORANGE)):
            vals = [p.loc[v, "ref"], p.loc[v, "nz"]]
            ax.bar(x + off, vals, width=w, color=c, label=VARIANT_LABELS[v])
        ax.set_xticks(x, ["ref 2050", "nz 2050"])
        ax.set_title(f"Road {pol}, kt", loc="left")
        ax.set_ylim(0, p[["ref", "nz"]].to_numpy().max() * 1.25)
        cut = (
            f"cut from ref to nz: native −{p.loc['native', 'reduction_pct']:.0f}%, "
            f"filled −{p.loc['filled', 'reduction_pct']:.0f}%"
        )
        ax.text(
            0.5, 0.96, cut, transform=ax.transAxes, ha="center", va="top", color=INK2, fontsize=8
        )
        _style(ax, "y")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper right", ncol=2, fontsize=8, bbox_to_anchor=(1, 0.995))
    fig.suptitle(
        "Road: untagged hybrids lower emission levels; the cut is similar",
        x=0.01,
        ha="left",
        fontsize=11,
        fontweight="semibold",
        color=INK,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    _save(fig, "fig10_policy_road", s[["pollutant", "variant", "ref", "nz", "reduction_pct"]])


# --------------------------------------------------------------------------- power table
KOREAN_POWER = [  # docs/gcam_kaist_ef_target_table.csv (not production-ready)
    ("coal (conv pul)", "NOx", "0.291 (2017 official); 0.102 (2022 fleet)"),
    ("coal (conv pul)", "SO2_2", "0.258 (2017 official); 0.110 (2022 fleet)"),
    ("gas (CC)", "NOx", "0.171 (2017 official gas-fleet average)"),
    ("gas (steam/CT)", "NOx", "0.171 (2017 official gas-fleet average)"),
    ("refined liquids (steam/CT)", "NOx", "0.711–0.727 (2015–2017)"),
    ("refined liquids (steam/CT)", "SO2_2", "1.264–1.367 (2015–2017)"),
]


def power_factor_table() -> None:
    x = pd.read_csv(COVERAGE / "driver_consistent_coef.csv")
    x = x[(x.scenario == "ref") & (x.sector == "electricity") & x.year.isin([2015, 2021])]
    rows = []
    for tech, pol, korean in KOREAN_POWER:
        q = (
            x[(x.technology == tech) & (x.native_pollutant == pol)]
            .set_index("year")
            .coef_native_units
        )
        rows.append(
            {
                "technology": tech,
                "pollutant": pol,
                "gcam_kaist_2015_kg_per_MWh": round(q[2015] * MWH_PER_EJ_FACTOR, 3),
                "gcam_kaist_2021_kg_per_MWh": round(q[2021] * MWH_PER_EJ_FACTOR, 3),
                "korean_reference_kg_per_MWh": korean,
            }
        )
    pd.DataFrame(rows).to_csv(DATA_DIR / "table_power_factors.csv", index=False)
    print("wrote data/table_power_factors.csv")


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    capss_vs_gcam(2015)
    capss_vs_gcam(2021)
    agreement_strip()
    mapping_search_table()
    gas_cc_vs_steamct()
    mobile_vs_stationary()
    coefficient_trajectories()
    base_year_swing()
    placeholder_shares()
    policy_power()
    policy_steel()
    policy_road()
    power_factor_table()


if __name__ == "__main__":
    main()
