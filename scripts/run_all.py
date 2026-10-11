"""Run all scenarios and sensitivities, collect GDX results into CSV files.

Usage:
    python scripts/run_all.py            # 6 core runs + sensitivities
    python scripts/run_all.py --core     # 6 core runs only

GAMS is located via GAMS_SYSDIR, the gamspy_base package or PATH
(see gdxio.py). Output: results/*.gdx, results/csv/*.csv, results/logs/*.lst
"""
import argparse
import subprocess
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gdxio import gams_exe, read_gdx  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
SCENARIOS = ["forest_first", "scarce_forest", "electrons_win"]
TIMINGS = ["ontime", "delay"]
REPORTS = ["REP_ELC", "REP_HET", "REP_BIO", "REP_BIOALLOC", "REP_BIOSUP", "REP_BLQ",
           "REP_AVF", "REP_DSL", "REP_FUELS", "REP_SAF", "REP_H2", "REP_EMIS", "REP_CO2BAL", "REP_CO2PRICE",
           "REP_ELCAVG", "REP_BIOPRICE", "REP_PEAK", "REP_COST", "REP_CAP", "REP_NCAP",
           "REP_CAL", "REP_CHECK", "REP_SCN"]


def run_list(core_only):
    runs = [dict(name=f"{s}_{t}", SCN=s, TIMING=t) for s in SCENARIOS for t in TIMINGS]
    if not core_only:
        for s in SCENARIOS:
            for r in (0.02, 0.07):
                runs.append(dict(name=f"{s}_ontime_r{int(r * 100):02d}", SCN=s,
                                 TIMING="ontime", DRATE=r))
            runs.append(dict(name=f"{s}_ontime_nonco2x2", SCN=s, TIMING="ontime", NONCO2=2))
    return runs


def run_gams(run):
    gdx = RES / f"{run['name']}.gdx"
    lst = RES / "logs" / f"{run['name']}.lst"
    args = [str(gams_exe()), str(ROOT / "model" / "core.gms"), f"o={lst}", "lo=0",
            f"curdir={ROOT / 'model'}", f"--OUT={gdx}"]
    args += [f"--{k}={v}" for k, v in run.items() if k != "name"]
    rc = subprocess.run(args).returncode
    if rc != 0:
        raise RuntimeError(f"GAMS failed for {run['name']} (rc={rc}), see {lst}")
    return gdx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--core", action="store_true", help="only the 6 core runs")
    a = ap.parse_args()
    (RES / "logs").mkdir(parents=True, exist_ok=True)
    (RES / "csv").mkdir(parents=True, exist_ok=True)

    frames = {name: [] for name in REPORTS}
    for run in run_list(a.core):
        print(f"running {run['name']} ...", flush=True)
        gdx = run_gams(run)
        data = read_gdx(gdx, REPORTS)
        for name, df in data.items():
            if df.empty:
                continue
            df = df.copy()
            df.insert(0, "run", run["name"])
            df.insert(1, "scenario", run["SCN"])
            df.insert(2, "timing", run["TIMING"])
            frames[name].append(df)

    for name, parts in frames.items():
        if parts:
            pd.concat(parts).to_csv(RES / "csv" / f"{name.lower()}.csv", index=False)

    checks = pd.concat(frames["REP_CHECK"]) if frames["REP_CHECK"] else pd.DataFrame()
    bad = checks[checks["value"].abs() > 1e-6] if not checks.empty else checks
    if not bad.empty:
        print("WARNING: failed model checks\n", bad.to_string(index=False))
    else:
        print("all model checks passed")
    print(f"results written to {RES / 'csv'}")


if __name__ == "__main__":
    main()
