"""Residual gross emissions: by sector, by innovation gap, and how far below the target.

1. Sectors: gross fossil CO2 in 2045 by sector for the six core runs
   (from results/csv/rep_co2prc.csv, written by run_all.py).
2. Innovation gaps: Forest first (on time) re-solved with one technology
   group unavailable (--NOTECH). The 2045 gross cap still binds, so a gap
   shows up as extra system cost, a higher CO2 price, a different residual
   mix or, if the cap cannot be met, as an infeasible run.
3. Frontier: the gross 2045 reduction tightened from 85% (the target) to
   100% (--RED45) for the three scenarios on time: the residual that is
   left when the model cannot go further, and what each step costs.

A run is "infeasible" when the LP has no solution: either already in the
calibration solve without CO2 constraints (a policy quota such as the
ReFuelEU synthetic-fuel share cannot be met) or only under the CO2 cap.
"unserved demand" means the cap is met only by leaving demand unserved
(VAR_DUM at its penalty price), so its cost is not a real system cost.

Usage: python scripts/residuals.py
Output: results/residuals/*.csv, results/tables/residuals.md,
        results/figures/fig5_residual_emissions.png
"""
import subprocess
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gdxio import gams_exe, read_gdx  # noqa: E402
from plots import FIG, INK2, PAL, SCN, SCN_LABEL, TAB  # noqa: E402
from run_all import RES  # noqa: E402

OUT = RES / "residuals"
YEAR = "2045"

SECTOR = {
    "CHP_WST": "Waste incineration (CHP)",
    "RD_OIL": "Road and machinery",
    "AV_OIL": "Domestic aviation",
    "IND_FOS": "Industry: fuels",
    "IND_FCS": "Industry: fuels",
    "STL_BF": "Industry: steel",
    "GT_NG": "Power and heat: fossil",
    "HET_FOS": "Power and heat: fossil",
}

# technology groups switched off one at a time (innovation not available)
GAPS = {
    "Hydrogen steel (DRI)": "STL_H2",
    "Industrial electrification": "IND_ELC",
    "Industrial CCS": "IND_FCS",
    "Advanced biofuels (FT, black liquor)": "BF_FT,BF_FTC,BF_BLG",
    "Bio-CCS at CHP": "CHP_BCS",
    "Bio-CCS at pulp mills": "IND_BLC",
    "E-kerosene": "EF_EKER",
}
FRONTIER = [0.85, 0.88, 0.90, 0.92, 0.94, 0.96, 0.98, 1.00]
REPORTS = ["REP_CO2PRC", "REP_CO2BAL", "REP_CO2PRICE", "REP_COST", "REP_CHECK"]


def solve(name, notech=None, **opts):
    """Run core.gms; return (report tables or None, reason)."""
    for i, p in enumerate((notech or "").split(",") if notech else []):
        opts["NOTECH" + (str(i + 1) if i else "")] = p
    gdx = OUT / "gdx" / f"{name}.gdx"
    lst = RES / "logs" / f"res_{name}.lst"
    args = [str(gams_exe()), str(RES.parent / "model" / "core.gms"), f"o={lst}", "lo=0",
            f"curdir={RES.parent / 'model'}", f"--OUT={gdx}"]
    args += [f"--{k}={v}" for k, v in opts.items()]
    if subprocess.run(args).returncode != 0:
        log = lst.read_text(encoding="utf-8", errors="replace") if lst.exists() else ""
        if "Calibration run not optimal" in log:
            return None, "infeasible without CO2 cap (policy quota)"
        if "Main run not optimal" in log:
            return None, "infeasible under CO2 cap"
        raise RuntimeError(f"GAMS failed for {name}, see {lst}")
    return read_gdx(gdx, REPORTS), ""


def summarise(name, result, **meta):
    rep, reason = result
    row = dict(run=name, **meta)
    if rep is None:
        return row | dict(status=reason)
    chk = rep["REP_CHECK"].set_index(rep["REP_CHECK"].columns[0]).value
    unserved = float(chk.get("unserved demand TWh", 0.0))
    cost = rep["REP_COST"].set_index(rep["REP_COST"].columns[0]).value
    bal = rep["REP_CO2BAL"]
    bal = bal[bal["T"] == YEAR].set_index(bal.columns[0]).value
    price = rep["REP_CO2PRICE"].set_index("T").value
    prc = rep["REP_CO2PRC"]
    prc = prc[prc["T"] == YEAR].assign(sector=lambda d: d.PRC.map(SECTOR))
    unmapped = prc[prc.sector.isna() & (prc.value.abs() > 1e-9)]
    if not unmapped.empty:
        raise ValueError(f"no sector for {sorted(unmapped.PRC)}")
    row |= dict(status="unserved demand" if unserved > 1e-6 else "optimal",
                npv=float(cost["NPV total"]),
                gross=float(bal.get("gross fossil (target scope)", 0.0)),
                stored=float(bal.get("BECCS stored", 0.0)),
                co2_price=float(price.get(YEAR, 0.0)))
    row |= prc.groupby("sector").value.sum().to_dict()
    return row


def sectors_core():
    d = pd.read_csv(RES / "csv" / "rep_co2prc.csv")
    d = d[(d["T"] == int(YEAR)) & d.run.isin([f"{s}_{t}" for s in SCN for t in ("ontime", "delay")])]
    d["sector"] = d.PRC.map(SECTOR)
    if d.sector.isna().any():
        raise ValueError(f"no sector for {sorted(d[d.sector.isna()].PRC.unique())}")
    return d.pivot_table(index="sector", columns="run", values="value", aggfunc="sum", fill_value=0)


def main():
    (OUT / "gdx").mkdir(parents=True, exist_ok=True)
    (RES / "logs").mkdir(parents=True, exist_ok=True)

    sectors = sectors_core()
    sectors.to_csv(OUT / "sectors_2045.csv")

    base = dict(SCN="forest_first", TIMING="ontime")
    gaps = [summarise("gap_none", solve("gap_none", **base), gap="none")]
    for label, techs in GAPS.items():
        name = "gap_" + techs.split(",")[0].lower()
        print(f"gap: {label} ...", flush=True)
        gaps.append(summarise(name, solve(name, notech=techs, **base), gap=label))
    gaps = pd.DataFrame(gaps)
    ref = gaps.loc[gaps.gap == "none", "npv"].iloc[0]
    gaps["extra_cost"] = (gaps["npv"] - ref).where(gaps.status == "optimal")
    gaps.to_csv(OUT / "innovation_gaps.csv", index=False)

    frontier = []
    for scn in SCN:
        for red in FRONTIER:
            name = f"frontier_{scn}_{round(red * 100)}"
            print(f"frontier: {scn} {red:.0%} ...", flush=True)
            frontier.append(summarise(name, solve(name, SCN=scn, TIMING="ontime", RED45=red),
                                      scenario=scn, reduction=red))
    frontier = pd.DataFrame(frontier)
    frontier.to_csv(OUT / "frontier.csv", index=False)

    write_table(sectors, gaps, frontier)
    plot(sectors, frontier)


def fmt(x, nd=1):
    return "" if pd.isna(x) else f"{round(x, nd) + 0.0:,.{nd}f}"


def write_table(sectors, gaps, frontier):
    lines = ["# Residual gross emissions (illustrative data)", "",
             f"## Gross fossil CO2 in {YEAR} by sector (Mt)", "",
             "| Sector | " + " | ".join(sectors.columns) + " |",
             "|---|" + "---|" * len(sectors.columns)]
    for sec, r in sectors.iterrows():
        lines.append(f"| {sec} | " + " | ".join(fmt(v, 2) for v in r) + " |")
    lines.append("| **Total** | " + " | ".join(fmt(v, 2) for v in sectors.sum()) + " |")

    secs = [c for c in sorted(set(SECTOR.values())) if c in gaps.columns]
    lines += ["", f"## Innovation gaps: Forest first, on time, one technology group unavailable ({YEAR})", "",
              "| Unavailable | Status | Extra cost (MEUR, NPV) | CO2 price (EUR/t) | BECCS stored (Mt) | "
              + " | ".join(secs) + " |",
              "|---|---|---|---|---|" + "---|" * len(secs)]
    for _, r in gaps.iterrows():
        if r.status != "optimal":  # unserved demand or no solution: the numbers are not a real system state
            r = r.where(r.index.isin(["gap", "status"]))
        lines.append(f"| {r.gap} | {r.status} | {fmt(r.get('extra_cost'), 0)} | {fmt(r.get('co2_price'), 0)} | "
                     f"{fmt(r.get('stored'), 2)} | " + " | ".join(fmt(r.get(s), 2) for s in secs) + " |")

    lines += ["", f"## Frontier: gross reduction in {YEAR} beyond the 85% target (on time)", "",
              "| Scenario | Reduction vs 1990 | Status | Gross CO2 (Mt) | Extra cost vs 85% (MEUR) | CO2 price (EUR/t) |",
              "|---|---|---|---|---|---|"]
    for scn, g in frontier.groupby("scenario", sort=False):
        ref = g.loc[g.reduction == 0.85, "npv"].iloc[0]
        g = g.assign(npv=g.npv.where(g.status == "optimal"))
        for _, r in g.iterrows():
            lines.append(f"| {SCN_LABEL[scn]} | {r.reduction:.0%} | {r.status} | {fmt(r.get('gross'), 2)} | "
                         f"{fmt(r.get('npv') - ref, 0)} | {fmt(r.get('co2_price'), 0)} |")
    (TAB / "residuals.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


def plot(sectors, frontier):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.6))
    runs = [r for r in sectors.columns if r.endswith("_ontime")]
    bottom = pd.Series(0.0, index=runs)
    for i, (sec, r) in enumerate(sectors[runs].iterrows()):
        a1.bar(range(len(runs)), r.values, bottom=bottom.values, color=PAL[i % len(PAL)], label=sec, width=0.6)
        bottom += r
    a1.set_xticks(range(len(runs)), [SCN_LABEL[r.rsplit("_", 1)[0]] for r in runs])
    a1.set_ylabel(f"Mt CO2 in {YEAR}")
    a1.set_title("Residual gross fossil CO2 by sector (on time)", loc="left", fontsize=10)
    a1.set_ylim(0, bottom.max() * 1.05)
    a1.legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=2)

    for i, scn in enumerate(SCN):
        g = frontier[(frontier.scenario == scn) & (frontier.status == "optimal")]
        ref = frontier.loc[(frontier.scenario == scn) & (frontier.reduction == 0.85), "npv"].iloc[0]
        a2.plot(g.reduction * 100, (g.npv - ref) / 1000, marker="o", color=PAL[i], label=SCN_LABEL[scn])
    first = frontier.loc[frontier.status != "optimal", "reduction"].min()
    a2.axvline(first * 100, color=INK2, lw=0.8, ls="--")
    a2.text(first * 100 - 0.1, 0.02, f"infeasible from {first:.0%}", transform=a2.get_xaxis_transform(), ha="right",
            fontsize=8, color=INK2, va="bottom")
    a2.set_xlabel("gross fossil CO2 reduction in 2045 vs 1990 (%)")
    a2.set_ylabel("extra system cost vs 85% (bn EUR, NPV)")
    a2.set_title("Going below the target: feasible runs only", loc="left", fontsize=10)
    a2.legend(frameon=False, fontsize=8)
    a2.tick_params(colors=INK2)
    fig.tight_layout()
    fig.savefig(FIG / "fig5_residual_emissions.png", dpi=150)


if __name__ == "__main__":
    main()
