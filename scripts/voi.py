"""Value of information on forest biomass availability (simplified version).

Biomass availability is the same for everyone until 2035 and is revealed in
2040: high (x1.2), base (x1.0) or low (x0.7), each with probability 1/3.

  WS   wait-and-see: each state solved with perfect foresight
  EV   expected-value plan: biomass fixed at its mean (x0.967)
  EEV  EV investments up to 2035 fixed, model re-solved in each state

EEV - WS is an upper bound on EVPI (= RP - WS), because the recourse
problem RP (two-stage stochastic optimum) costs at most EEV. RP and VSS
(= EEV - RP) need model/stochastic.gms, which exceeds the GAMS demo limits.

Usage: python scripts/voi.py
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gdxio import read_gdx  # noqa: E402
from run_all import RES, run_gams  # noqa: E402

STATES = {"high": 1.2, "base": 1.0, "low": 0.7}
PROB = {s: 1 / 3 for s in STATES}


def npv(gdx):
    c = read_gdx(gdx, ["REP_COST"])["REP_COST"]
    return float(c.loc[c.uni == "NPV total", "value"].iloc[0])


def ncap_first_stage(gdx):
    n = read_gdx(gdx, ["REP_NCAP"])["REP_NCAP"]
    n["T"] = n["T"].astype(int)
    return n[n["T"] <= 2035].groupby("PRC").value.sum()


def bio_alloc(gdx, year):
    b = read_gdx(gdx, ["REP_BIOALLOC"])["REP_BIOALLOC"]
    b["T"] = b["T"].astype(int)
    return b[b["T"] == year].set_index("BCAT").value


def main():
    (RES / "logs").mkdir(parents=True, exist_ok=True)
    mean = sum(PROB[s] * m for s, m in STATES.items())
    base = dict(SCN="voi_base", TIMING="ontime")

    ev = run_gams(dict(name="voi_ev", BIO40=round(mean, 4), **base))
    ws = {s: run_gams(dict(name=f"voi_ws_{s}", BIO40=m, **base)) for s, m in STATES.items()}
    eev = {s: run_gams(dict(name=f"voi_eev_{s}", BIO40=m, FIX1=ev, **base))
           for s, m in STATES.items()}

    cost = pd.DataFrame({"WS": {s: npv(g) for s, g in ws.items()},
                         "EEV": {s: npv(g) for s, g in eev.items()}})
    cost["regret (EEV - WS)"] = cost["EEV"] - cost["WS"]
    exp_ws = sum(PROB[s] * cost.loc[s, "WS"] for s in STATES)
    exp_eev = sum(PROB[s] * cost.loc[s, "EEV"] for s in STATES)
    evpi_ub = exp_eev - exp_ws

    first = pd.DataFrame({f"WS {s}": ncap_first_stage(g) for s, g in ws.items()})
    first["EV plan"] = ncap_first_stage(ev)
    first = first.fillna(0)
    first["range across states"] = first[[f"WS {s}" for s in STATES]].max(axis=1) - \
        first[[f"WS {s}" for s in STATES]].min(axis=1)
    first = first[first.abs().sum(axis=1) > 1e-6].sort_values("range across states", ascending=False)

    alloc = pd.DataFrame({**{f"WS {s}": bio_alloc(g, 2045) for s, g in ws.items()},
                          **{f"EEV {s}": bio_alloc(g, 2045) for s, g in eev.items()}}).fillna(0)

    out = RES / "csv"
    out.mkdir(exist_ok=True)
    cost.to_csv(out / "voi_cost.csv")
    first.to_csv(out / "voi_first_stage_ncap.csv")
    alloc.to_csv(out / "voi_bioalloc_2045.csv")

    lines = ["# Value of information on forest biomass availability", "",
             f"States revealed in 2040: {', '.join(f'{s} x{m}' for s, m in STATES.items())}, "
             "probability 1/3 each.", "",
             "| State | WS cost (MEUR NPV) | EEV cost (MEUR NPV) | Regret of the EV plan (MEUR) |",
             "|---|---|---|---|"]
    for s in STATES:
        lines.append(f"| {s} | {cost.loc[s, 'WS']:,.0f} | {cost.loc[s, 'EEV']:,.0f} | "
                     f"{cost.loc[s, 'regret (EEV - WS)']:,.0f} |")
    lines += ["", f"Expected WS: {exp_ws:,.0f} MEUR; expected EEV: {exp_eev:,.0f} MEUR.",
              f"Upper bound on EVPI (EEV - WS): **{evpi_ub:,.0f} MEUR** "
              f"({100 * evpi_ub / exp_ws:.2f}% of expected system cost).", "",
              "## First-stage investments (2030-2035, GW or Mt/yr) under perfect information", "",
              "| Process | " + " | ".join(first.columns) + " |",
              "|---|" + "---|" * len(first.columns)]
    for prc, row in first.iterrows():
        lines.append(f"| {prc} | " + " | ".join(f"{v:.2f}" for v in row) + " |")
    lines += ["", "## Forest biomass allocation in 2045 (TWh)", "",
              "| Use | " + " | ".join(alloc.columns) + " |", "|---|" + "---|" * len(alloc.columns)]
    for cat, row in alloc.iterrows():
        lines.append(f"| {cat} | " + " | ".join(f"{v:.1f}" for v in row) + " |")
    (RES / "tables").mkdir(exist_ok=True)
    (RES / "tables" / "voi.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
