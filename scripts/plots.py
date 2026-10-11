"""Figures and tables from results/csv (run scripts/run_all.py first).

Output: results/figures/*.png, results/tables/*.md
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "results" / "csv"
FIG = ROOT / "results" / "figures"
TAB = ROOT / "results" / "tables"

SCN = ["forest_first", "scarce_forest", "electrons_win"]
SCN_LABEL = {"forest_first": "Forest first", "scarce_forest": "Scarce forest",
             "electrons_win": "Electrons win"}
TIMING_LABEL = {"ontime": "on time (2030)", "delay": "delayed (2040)"}
CORE = [f"{s}_{t}" for s in SCN for t in ("ontime", "delay")]
YEARS = [2025, 2030, 2035, 2040, 2045, 2050]

# reference categorical palette, fixed order (dataviz skill, light mode)
PAL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"

plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2,
    "ytick.color": INK2, "text.color": INK, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.8, "axes.axisbelow": True, "axes.spines.top": False,
    "axes.spines.right": False, "font.size": 9, "axes.titlesize": 10,
    "legend.frameon": False,
})


def load(name):
    return pd.read_csv(CSV / f"{name}.csv")


def run_label(run):
    s, t = run.rsplit("_", 1)
    return SCN_LABEL[s] + "\n" + ("on time" if t == "ontime" else "delayed")


def legend_union(axes):
    """Handles and labels of all axes, each label once (in order of appearance)."""
    seen = {}
    for ax in axes:
        for h, lab in zip(*ax.get_legend_handles_labels()):
            seen.setdefault(lab, h)
    return list(seen.values()), list(seen.keys())


def stacked(ax, df, cats, colors, x, width=0.75):
    """Stacked bars with a thin surface-coloured gap between segments."""
    bottom = pd.Series(0.0, index=df.index)
    for cat, col in zip(cats, colors):
        if cat not in df.columns:
            continue
        ax.bar(x, df[cat], width, bottom=bottom, color=col, label=cat,
               edgecolor=SURF, linewidth=1.0)
        bottom += df[cat]


# ---------------------------------------------------------------- figure 1
def fig_biomass():
    d = load("rep_bioalloc")
    cats = {"BIOFUEL": "Biofuels (FT)", "BIOF_CCS": "Biofuels + CO2 capture",
            "DH": "District heating and CHP", "DH_CCS": "CHP + CO2 capture (BECCS)",
            "INDUSTRY": "Industry"}
    d = d[d.run.isin(CORE)]
    fig, axes = plt.subplots(2, 3, figsize=(10, 5.6), sharey=True)
    for j, s in enumerate(SCN):
        for i, t in enumerate(("ontime", "delay")):
            ax = axes[i, j]
            sub = d[d.run == f"{s}_{t}"].pivot_table(index="T", columns="BCAT", values="value")
            sub = sub.reindex(YEARS).fillna(0).rename(columns=cats)
            stacked(ax, sub, list(cats.values()), PAL, range(len(YEARS)))
            ax.set_xticks(range(len(YEARS)), YEARS)
            ax.set_title(f"{SCN_LABEL[s]}, technologies {TIMING_LABEL[t]}")
            if j == 0:
                ax.set_ylabel("Forest biomass use (TWh/yr)")
    h, lab = legend_union(axes.flat)
    fig.legend(h, lab, loc="lower center", ncol=5, bbox_to_anchor=(0.5, -0.01))
    fig.suptitle("Allocation of Swedish forest biomass by use, scenario and period", x=0.01,
                 ha="left", fontsize=11)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(FIG / "fig1_biomass_allocation.png", dpi=160)
    plt.close(fig)


# ---------------------------------------------------------------- figure 2
def fig_power():
    e = load("rep_elc")
    groups = {"ELC_HYD": "Hydro", "ELC_NUC": "Nuclear", "ELC_WON": "Wind",
              "ELC_WOF": "Wind", "ELC_SOL": "Solar", "CHP_BIO": "CHP (biomass, waste)",
              "CHP_BCS": "CHP (biomass, waste)", "CHP_WST": "CHP (biomass, waste)",
              "IND_BLQ": "Industrial CHP", "IND_BLC": "Industrial CHP",
              "GT_BIO": "Gas turbines", "GT_H2": "Gas turbines", "GT_NG": "Gas turbines",
              "ELC_IMP": "Imports"}
    order = ["Hydro", "Nuclear", "Wind", "Solar", "CHP (biomass, waste)", "Industrial CHP",
             "Gas turbines", "Imports"]
    e = e[e.run.isin(CORE) & (e["T"] == 2045)].copy()
    e["grp"] = e.PRC.map(groups)
    gen = e.pivot_table(index="run", columns="grp", values="value", aggfunc="sum")
    gen = gen.reindex(CORE).fillna(0)

    p = load("rep_cap")
    p = p[p.run.isin([f"{s}_ontime" for s in SCN]) & p.PRC.isin(["GT_BIO", "GT_H2", "GT_NG", "DR_ELC"])]
    gt_lab = {"GT_BIO": "Liquid biofuel GT", "GT_H2": "Hydrogen GT", "GT_NG": "Fossil GT (existing)",
              "DR_ELC": "Demand response"}
    ymax = p.groupby(["run", "T"])["value"].sum().max()

    fig = plt.figure(figsize=(13, 4.8))
    gs = fig.add_gridspec(1, 4, width_ratios=[2.8, 1, 1, 1], wspace=0.3)
    a1 = fig.add_subplot(gs[0])
    stacked(a1, gen, order, PAL, range(len(CORE)))
    a1.set_xticks(range(len(CORE)), [run_label(r) for r in CORE], fontsize=6.5)
    a1.set_ylabel("TWh")
    a1.set_title("Electricity generation in 2045")
    a1.legend(loc="upper left", bbox_to_anchor=(0, -0.16), ncol=4, fontsize=8)

    axes = [fig.add_subplot(gs[k + 1]) for k in range(3)]
    for k, s in enumerate(SCN):
        ax = axes[k]
        sub = p[p.run == f"{s}_ontime"].pivot_table(index="T", columns="PRC", values="value")
        sub = sub.reindex(YEARS).fillna(0).rename(columns=gt_lab)
        stacked(ax, sub, list(gt_lab.values()), [PAL[1], PAL[6], PAL[7], PAL[3]], range(len(YEARS)), 0.7)
        ax.set_xticks(range(len(YEARS)), [str(y)[2:] if i else str(y) for i, y in enumerate(YEARS)])
        ax.set_ylim(0, ymax * 1.1)
        ax.set_title(SCN_LABEL[s], fontsize=9)
        if k == 0:
            ax.set_ylabel("GW installed")
        else:
            ax.set_yticklabels([])
    axes[1].text(0.5, 1.13, "Gas turbines and demand response for the peak reserve (technologies on time)",
                 transform=axes[1].transAxes, ha="center", fontsize=10)
    h, lab = legend_union(axes)
    axes[0].legend(h, lab, loc="upper left", bbox_to_anchor=(0, -0.1), ncol=4, fontsize=8)
    fig.subplots_adjust(left=0.05, right=0.99, top=0.86, bottom=0.27)
    fig.savefig(FIG / "fig2_power_and_peak_turbines.png", dpi=160)
    plt.close(fig)


# ---------------------------------------------------------------- figure 3
def fig_heat():
    h = load("rep_het")
    groups = {"HET_HP": "Heat pumps", "CHP_BIO": "Biomass CHP", "CHP_BCS": "Biomass CHP + CO2 capture",
              "CHP_WST": "Waste CHP", "HET_BOB": "Biomass boilers",
              "HET_XS": "Industrial excess heat", "BF_FT": "Biofuel and e-fuel plants",
              "BF_FTC": "Biofuel and e-fuel plants", "EF_EKER": "Biofuel and e-fuel plants",
              "HET_EB": "Electric and fossil boilers", "HET_FOS": "Electric and fossil boilers"}
    order = ["Heat pumps", "Biomass CHP", "Biomass CHP + CO2 capture", "Waste CHP",
             "Biomass boilers", "Industrial excess heat", "Biofuel and e-fuel plants",
             "Electric and fossil boilers"]
    h = h[h.run.isin(CORE)].copy()
    h["grp"] = h.PRC.map(groups)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), gridspec_kw={"width_ratios": [1, 1.1]})
    ref = h[h.run == "forest_first_ontime"].pivot_table(index="T", columns="grp", values="value",
                                                        aggfunc="sum").reindex(YEARS).fillna(0)
    stacked(axes[0], ref, order, PAL, range(len(YEARS)))
    axes[0].set_xticks(range(len(YEARS)), YEARS)
    axes[0].set_ylabel("District heat supply (TWh)")
    axes[0].set_title("Forest first, technologies on time")
    y45 = h[h["T"] == 2045].pivot_table(index="run", columns="grp", values="value",
                                         aggfunc="sum").reindex(CORE).fillna(0)
    stacked(axes[1], y45, order, PAL, range(len(CORE)))
    axes[1].set_xticks(range(len(CORE)), [run_label(r) for r in CORE], fontsize=7)
    axes[1].set_title("All scenarios, 2045")
    hd, lab = axes[0].get_legend_handles_labels()
    fig.legend(hd, lab, loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.01))
    fig.suptitle("District heating supply by source", x=0.01, ha="left", fontsize=11)
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    fig.savefig(FIG / "fig3_district_heat.png", dpi=160)
    plt.close(fig)


# ---------------------------------------------------------------- figure 4
def fig_cost_co2():
    c = load("rep_cost")
    c = c[(c.uni == "NPV total") & c.run.isin(CORE)].set_index("run").value.reindex(CORE)
    base = c["forest_first_ontime"]
    q = load("rep_co2price")
    q = q[q.run.isin(CORE)]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
    cols = [PAL[SCN.index(r.rsplit("_", 1)[0])] for r in CORE]
    a1.bar(range(len(CORE)), (c - base) / 1000, 0.6, color=cols, edgecolor=SURF)
    for i, v in enumerate((c - base) / 1000):
        a1.text(i, v + (0.1 if v >= 0 else -0.3), f"{v:+.1f}", ha="center", fontsize=8, color=INK)
    a1.set_xticks(range(len(CORE)), [run_label(r) for r in CORE], fontsize=7)
    a1.set_ylabel("bn EUR (NPV 2025-2054, 4%)")
    a1.set_title("System cost relative to Forest first, on time")
    a1.axhline(0, color=INK2, linewidth=0.8)
    for k, s in enumerate(SCN):
        for t, ls in (("ontime", "-"), ("delay", "--")):
            sub = q[q.run == f"{s}_{t}"].sort_values("T")
            a2.plot(sub["T"], sub.value, ls, color=PAL[k], linewidth=2, marker="o", markersize=4,
                    label=f"{SCN_LABEL[s]}, {TIMING_LABEL[t]}")
    a2.set_xticks(YEARS[1:])
    a2.set_ylabel("EUR per t CO2")
    a2.set_title("CO2 shadow price (gross cap + net-zero constraint)")
    a2.legend(fontsize=7, loc="upper left")
    fig.tight_layout()
    fig.savefig(FIG / "fig4_cost_and_co2_price.png", dpi=160)
    plt.close(fig)


# ---------------------------------------------------------------- table 6
def table_cobenefits():
    e = load("rep_emis")
    e = e[e.run.isin(CORE) & e.EM.isin(["NOX", "PM25"])]
    piv = e.pivot_table(index="run", columns=["EM", "T"], values="value").reindex(CORE)
    lines = ["| Scenario | NOx 2025 (kt) | NOx 2045 (kt) | PM2.5 2025 (kt) | PM2.5 2045 (kt) |",
             "|---|---|---|---|---|"]
    for r in CORE:
        row = piv.loc[r]
        lines.append(f"| {run_label(r).replace(chr(10), ', ')} | {row[('NOX', 2025)]:.1f} | "
                     f"{row[('NOX', 2045)]:.1f} | {row[('PM25', 2025)]:.1f} | {row[('PM25', 2045)]:.1f} |")
    (TAB / "co_benefits.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def table_calibration():
    c = load("rep_cal")
    c = c[c.run == "forest_first_ontime"].pivot_table(index="CALITEM", columns="uni", values="value")
    lines = ["| Item | Statistics (TWh) | Model 2025 (TWh) | Difference (%) |", "|---|---|---|---|"]
    for item, row in c.iterrows():
        lines.append(f"| {item} | {row['STAT']:.1f} | {row['model']:.1f} | {row['diff_pct']:+.1f} |")
    (TAB / "calibration.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    FIG.mkdir(parents=True, exist_ok=True)
    TAB.mkdir(parents=True, exist_ok=True)
    fig_biomass()
    fig_power()
    fig_heat()
    fig_cost_co2()
    table_cobenefits()
    table_calibration()
    print(f"figures in {FIG}, tables in {TAB}")
