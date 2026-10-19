"""Export model results to the IAMC format and check them against a small protocol.

Reads results/csv/*.csv (written by run_all.py) and builds one pyam
IamDataFrame (model, scenario, region, variable, unit, year), using IAMC
variable names where a common one exists (AR6 scenario template style) and
model-specific names otherwise. Energy flows are converted from TWh/yr to
EJ/yr with pyam's unit registry.

Protocol checks (the kind a modelling protocol applies to scenario submissions):
  1. completeness: every required variable is reported for every scenario
  2. aggregation: Secondary Energy|Electricity equals the sum of its components
  3. gross target: gross fossil CO2 stays within the cap of the 85% target
  4. net zero: net CO2 is at most zero from 2045
  5. calibration: 2025 electricity within 5% of SCB statistics

Usage: python scripts/to_iamc.py
Output: results/iamc/sweden_times_mini_iamc.xlsx, .csv and checks.md
"""
from pathlib import Path

import pandas as pd
import pyam

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "results" / "csv"
OUT = ROOT / "results" / "iamc"
MODEL = "sweden-biomass-times-mini"
REGION = "Sweden"
TOL = 1e-6
YEARS = [2025, 2030, 2035, 2040, 2045, 2050]
RUNS = []

ELC = {
    "ELC_HYD": "Hydro",
    "ELC_NUC": "Nuclear",
    "ELC_SOL": "Solar",
    "ELC_WON": "Wind|Onshore",
    "ELC_WOF": "Wind|Offshore",
    "CHP_BIO": "Biomass|w/o CCS",
    "GT_BIO": "Biomass|w/o CCS",
    "IND_BLQ": "Biomass|w/o CCS",
    "CHP_BCS": "Biomass|w/ CCS",
    "GT_NG": "Gas|w/o CCS",
    "GT_H2": "Hydrogen",
    "CHP_WST": "Other",
}
# not generation: imports and demand response are reported separately
ELC_OTHER = {"ELC_IMP": "Trade|Secondary Energy|Electricity|Volume"}

BIOALLOC = {
    "DH": "District Heating|w/o CCS",
    "DH_CCS": "District Heating|w/ CCS",
    "INDUSTRY": "Industry",
    "BIOF_CCS": "Biofuels|w/ CCS",
}

REQUIRED = [
    "Emissions|CO2",
    "Emissions|CO2|Energy and Industrial Processes",
    "Carbon Sequestration|CCS|Biomass",
    "Secondary Energy|Electricity",
    "Price|Carbon",
]


def rows(df, variable, unit, years=None):
    """One IAMC variable from a report table. GDX files store no zeros, so a
    quantity missing for a run and year is written as 0 over `years`."""
    out = df.drop(columns="scenario", errors="ignore").rename(columns={"run": "scenario", "T": "year"})
    out = out.groupby(["scenario", "year"]).value.sum()
    if years is not None:
        full = pd.MultiIndex.from_product([RUNS, years], names=["scenario", "year"])
        out = out.reindex(full, fill_value=0.0)
    out = out.reset_index()
    out["variable"] = variable
    out["unit"] = unit
    return out


def build():
    global RUNS
    RUNS = sorted(pd.read_csv(CSV / "rep_scn.csv").run.unique())
    frames = []

    co2 = pd.read_csv(CSV / "rep_co2bal.csv")
    for uni, var in [("gross fossil (target scope)", "Emissions|CO2|Energy and Industrial Processes"),
                     ("net", "Emissions|CO2"),
                     ("BECCS stored", "Carbon Sequestration|CCS|Biomass")]:
        frames.append(rows(co2[co2.uni == uni], var, "Mt CO2/yr", YEARS))
    # the cap starts in 2030
    frames.append(rows(co2[co2.uni == "gross cap"],
                       "Policy|Cap|Emissions|CO2|Energy and Industrial Processes", "Mt CO2/yr"))

    emis = pd.read_csv(CSV / "rep_emis.csv")
    for em, var, unit in [("NOX", "Emissions|NOx", "kt NOx/yr"), ("PM25", "Emissions|PM2.5", "kt PM2.5/yr")]:
        frames.append(rows(emis[emis.EM == em], var, unit, YEARS))

    elc = pd.read_csv(CSV / "rep_elc.csv")
    gen = elc[elc.PRC.isin(ELC)].assign(PRC=lambda d: d.PRC.map(ELC))
    # the total is summed here from the model output, independent of the components check
    frames.append(rows(gen, "Secondary Energy|Electricity", "TWh/yr", YEARS))
    for tech, d in gen.groupby("PRC"):
        frames.append(rows(d, f"Secondary Energy|Electricity|{tech}", "TWh/yr", YEARS))
    for prc, var in ELC_OTHER.items():
        frames.append(rows(elc[elc.PRC == prc], var, "TWh/yr", YEARS))

    bio = pd.read_csv(CSV / "rep_bioalloc.csv")
    for cat, name in BIOALLOC.items():
        frames.append(rows(bio[bio.BCAT == cat], f"Primary Energy|Biomass|Forest|{name}", "TWh/yr", YEARS))

    price = pd.read_csv(CSV / "rep_co2price.csv")
    # a shadow price, defined from 2030; zero where the targets do not bind
    frames.append(rows(bio[bio.BCAT.isin(BIOALLOC)], "Primary Energy|Biomass|Forest", "TWh/yr", YEARS))
    frames.append(rows(price, "Price|Carbon", "EUR/t CO2", YEARS[1:]))

    data = pd.concat(frames, ignore_index=True)
    data["model"] = MODEL
    data["region"] = REGION
    df = pyam.IamDataFrame(data)

    # TWh/yr -> EJ/yr for all energy variables
    df = df.convert_unit("TWh/yr", to="EJ/yr")
    return df


def check(df):
    results = []

    missing = df.require_data(variable=REQUIRED)
    results.append(("completeness", missing is None,
                    "all required variables for all scenarios" if missing is None
                    else missing.to_string()))

    for total in ["Secondary Energy|Electricity", "Primary Energy|Biomass|Forest"]:
        parts = [v for v in df.variable if v.startswith(total + "|")]
        agg = df.check_aggregate(total, components=parts, rtol=1e-6)
        results.append((f"aggregation: {total}", agg is None,
                        f"total = sum of {len(parts)} components" if agg is None else agg.to_string()))

    gross = df.filter(variable="Emissions|CO2|Energy and Industrial Processes", year=range(2030, 2051))
    cap = df.filter(variable="Policy|Cap|Emissions|CO2|Energy and Industrial Processes", year=range(2030, 2051))
    diff = (gross.timeseries().droplevel(["variable"]) - cap.timeseries().droplevel(["variable"]))
    worst = diff.max().max()
    results.append(("gross target", worst <= TOL, f"largest gross minus cap: {worst:.3g} Mt CO2/yr"))

    net = df.filter(variable="Emissions|CO2", year=[2045, 2050])
    n_net = len(net.series)
    worst_net = net.timeseries().max().max()
    results.append(("net zero", n_net == 2 * len(df.scenario) and worst_net <= TOL,
                    f"largest net CO2 in 2045 and 2050: {worst_net:.3g} Mt CO2/yr ({n_net} values)"))

    cal = pd.read_csv(CSV / "rep_cal.csv").pivot_table(index=["run", "CALITEM"], columns="uni", values="value")
    dev = (cal["model"] / cal["STAT"] - 1).abs()
    worst_cal = dev.xs("ELC_TOTAL", level="CALITEM").max()
    results.append(("calibration", worst_cal <= 0.05, f"largest deviation of total 2025 electricity: {worst_cal:.1%}"))
    return results


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    df = build()
    df.to_excel(OUT / "sweden_times_mini_iamc.xlsx")
    df.to_csv(OUT / "sweden_times_mini_iamc.csv")

    lines = ["# Protocol checks on the IAMC export", "",
             f"{len(df.scenario)} scenarios, {len(df.variable)} variables, years {min(df.year)} to {max(df.year)}.", "",
             "| Check | Result | Detail |", "|---|---|---|"]
    ok = True
    for name, passed, detail in check(df):
        ok &= passed
        lines.append(f"| {name} | {'pass' if passed else 'FAIL'} | {detail} |")
    (OUT / "checks.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
