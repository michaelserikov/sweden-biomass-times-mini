"""Version 0.2: hydrogen, biomethane and industrial decarbonisation.

1. Hydrogen storage: the three scenarios (on time) re-solved without a
   hydrogen store (--NOH2STG=1). The difference in system cost is the value
   of seasonal storage in this system.
2. Abatement cost curve: Forest first and Electrons win (on time) solved in
   CO2 price mode (--CO2P) for 2045 prices from 80 to 500 EUR/t, with and
   without payment for stored biogenic CO2 (--NEGCR). The response of gross
   emissions, stored CO2, high-temperature heat and biomethane to the price
   is a model-based marginal abatement cost curve.
3. Biogenic carbon: the three scenarios under the cap with a carbon debt on
   additional forest biomass (--BIOC = 0.3 and 0.6).
4. Cost of avoided CO2 by technology at the 2045 shadow prices of Forest
   first (on time): levelised cost of an option against its fossil reference
   divided by the CO2 it avoids (stored biogenic CO2 counts as avoided).

Usage: python scripts/hydrogen_biomethane.py   (after scripts/run_all.py)
Output: results/g1/*.csv, results/tables/hydrogen_biomethane.md,
        results/figures/fig7_*.png to fig9_*.png
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

ROOT = RES.parent
OUT = RES / "g1"
YEAR = "2045"
PRICES = [80, 100, 125, 150, 200, 250, 300, 400, 500]
REPORTS = ["REP_COST", "REP_CO2BAL", "REP_CO2PRICE", "REP_H2", "REP_H2SEAS", "REP_H2PRICE",
           "REP_BMG", "REP_IHT", "REP_CAP", "REP_COMPRICE", "REP_BIOALLOC", "REP_BIOSUP",
           "REP_CHECK"]


def solve(name, **opts):
    gdx = OUT / "gdx" / f"{name}.gdx"
    lst = RES / "logs" / f"g1_{name}.lst"
    args = [str(gams_exe()), str(ROOT / "model" / "core.gms"), f"o={lst}", "lo=0",
            f"curdir={ROOT / 'model'}", f"--OUT={gdx}"]
    args += [f"--{k}={v}" for k, v in opts.items()]
    if subprocess.run(args).returncode != 0:
        raise RuntimeError(f"GAMS failed for {name}, see {lst}")
    d = read_gdx(gdx, REPORTS)
    bad = d["REP_CHECK"]
    if not bad.empty and (bad.value.abs() > 1e-6).any():
        raise RuntimeError(f"model checks failed for {name}: {bad.to_dict('records')}")
    return d


def core(name):
    return read_gdx(RES / f"{name}.gdx", REPORTS)


def val(d, rep, key=None, col=None, year=YEAR):
    df = d[rep]
    if df.empty:
        return 0.0
    if "T" in df.columns and year is not None:
        df = df[df["T"] == year]
    if key is not None:
        df = df[df[col] == key]
    return float(df.value.sum())


def npv(d, item="NPV total"):
    return val(d, "REP_COST", item, "uni", None)


# ---------------------------------------------------------------- 1. storage
def storage_runs():
    rows = []
    for s in SCN:
        base, nos = core(f"{s}_ontime"), solve(f"{s}_noh2stg", SCN=s, TIMING="ontime", NOH2STG=1)
        seas = base["REP_H2SEAS"]
        lev = seas[(seas.uni == "storage level") & (seas["T"] == YEAR)]
        rows.append({
            "scenario": SCN_LABEL[s],
            "H2 demand 2045 (TWh)": -val(base, "REP_H2", "H2_ELZ", "PRC"),
            "electrolysis (GW)": val(base, "REP_CAP", "H2_ELZ", "PRC"),
            "electrolysis without store (GW)": val(nos, "REP_CAP", "H2_ELZ", "PRC"),
            "store (TWh)": val(base, "REP_CAP", "H2_STG", "PRC"),
            "max level (TWh)": float(lev.value.max()) if not lev.empty else 0.0,
            "H2 price (EUR/MWh)": val(base, "REP_COMPRICE", "hydrogen", "uni"),
            "H2 price without store": val(nos, "REP_COMPRICE", "hydrogen", "uni"),
            "value of storage (MEUR NPV)": npv(nos) - npv(base),
        })
        for c in (0.25, 0.1):
            ch = solve(f"{s}_h2stg{int(c * 100):02d}", SCN=s, TIMING="ontime", H2STGC=c)
            rows[-1][f"store at x{c} cost (TWh)"] = val(ch, "REP_CAP", "H2_STG", "PRC")
            rows[-1][f"value at x{c} cost (MEUR NPV)"] = npv(nos) - npv(ch)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- 2. MAC
def mac_runs():
    cases = [("forest_first", 1), ("forest_first", 0), ("electrons_win", 1)]
    rows = []
    for s, neg in cases:
        for p in PRICES:
            name = f"mac_{s}_p{p}_neg{neg}"
            d = solve(name, SCN=s, TIMING="ontime", CO2P=p, NEGCR=neg)
            r = {"scenario": s, "NEGCR": neg, "price": p,
                 "gross fossil CO2": val(d, "REP_CO2BAL", "gross fossil (target scope)", "uni"),
                 "stored CO2": val(d, "REP_CO2BAL", "BECCS stored", "uni"),
                 "system cost excl. CO2": npv(d, "NPV system cost excl. CO2"),
                 "H2": -val(d, "REP_H2", "H2_ELZ", "PRC"),
                 "H2 store": val(d, "REP_CAP", "H2_STG", "PRC")}
            for p_ in ("IHT_FOS", "IHT_H2", "IHT_ELC"):
                r[p_] = val(d, "REP_IHT", p_, "PRC")
            for p_ in ("BG_AD", "BG_SNG", "GAS_BMG", "RD_BMG"):
                r[p_] = val(d, "REP_BMG", p_, "PRC")
            r["forest biomass"] = val(d, "REP_BIOSUP")
            rows.append(r)
    df = pd.DataFrame(rows)
    df["net CO2"] = df["gross fossil CO2"] - df["stored CO2"]
    return df


# ---------------------------------------------------------------- 3. biogenic carbon
def bioc_runs():
    rows = []
    for s in SCN:
        for f in (0.0, 0.3, 0.6):
            d = core(f"{s}_ontime") if f == 0 else solve(f"{s}_bioc{int(f * 10)}", SCN=s,
                                                          TIMING="ontime", BIOC=f)
            alloc = d["REP_BIOALLOC"]
            alloc = alloc[alloc["T"] == YEAR].set_index("BCAT").value
            rows.append({"scenario": SCN_LABEL[s], "carbon debt share": f,
                         "forest biomass (TWh)": val(d, "REP_BIOSUP"),
                         "of which CHP with capture": alloc.get("DH_CCS", 0.0),
                         "carbon debt (Mt)": val(d, "REP_CO2BAL", "biogenic carbon debt", "uni"),
                         "stored CO2 (Mt)": val(d, "REP_CO2BAL", "BECCS stored", "uni"),
                         "biomethane (TWh)": val(d, "REP_BMG", "BG_AD", "PRC") + val(d, "REP_BMG", "BG_SNG", "PRC"),
                         "CO2 price (EUR/t)": val(d, "REP_CO2PRICE"),
                         "NPV": npv(d)})
    df = pd.DataFrame(rows)
    df["extra cost (MEUR NPV)"] = df.NPV - df.groupby("scenario").NPV.transform("first")
    return df.drop(columns="NPV")


# ---------------------------------------------------------------- 4. technology cost
FUEL = {"NG": 35.0, "COA": 15.0, "OIL_JET": 55.0, "OIL_DSL": 60.0}
EF = {"NG": 0.202, "COA": 0.340, "OIL_JET": 0.257, "OIL_DSL": 0.267}
STORE = 50.0       # EUR/t, transport and storage of captured CO2 (CCS_STG)
LIQ = 20.0         # EUR/t, CC_BGP liquefaction, plus 0.12 MWh electricity per t


def levelised(prc, main, price, proc, flows, swap=None):
    """EUR per unit of the main output and fossil CO2 (t) per unit, incl. stored CO2."""
    p = proc.loc[prc]
    crf = 0.04 / (1 - 1.04 ** -p.NCAP_TLIFE) if p.NCAP_TLIFE > 1 else 0
    cap = (p.NCAP_COST * crf + p.NCAP_FOM) / (p.PRC_CAPACT * p.NCAP_AF) if p.CAPF else 0
    f = flows[flows.PRC == prc]
    mout = float(f[(f.COM == main) & (f.IO == "OUT")].value.sum())
    cost, co2 = cap + p.ACT_COST, 0.0
    for _, r in f.iterrows():
        com = swap.get(r.COM, r.COM) if swap else r.COM
        if r.IO == "IN":
            cost += r.value * price.get(com, 0.0)
            co2 += r.value * EF.get(com, 0.0) * (0.1 if prc == "IND_FCS" else 1)
        elif r.COM == "CO2_CAP":
            cost += r.value * STORE
            co2 -= r.value
        elif r.COM != main:
            cost -= r.value * price.get(r.COM, 0.0)
    return cost / mout, co2 / mout


def abatement_table():
    proc = pd.read_csv(ROOT / "data" / "processes.csv").set_index("PRC")
    flows = pd.read_csv(ROOT / "data" / "flows.csv", comment="*", header=None,
                        names=["PRC", "COM", "IO", "value"])
    cp = core("forest_first_ontime")["REP_COMPRICE"]
    cp = cp[cp["T"] == YEAR].set_index("uni").value
    price = dict(FUEL, ELC=cp["electricity flat"], H2=cp["hydrogen"], BMG=cp["biomethane price"],
                 BIO_SOL=cp["forest biomass"], HET=cp["district heat"])
    cases = [  # label, option, reference, main output, unit, swap of input commodity
        ("Hydrogen direct reduction steel", "STL_H2", "STL_BF", "STL", "EUR/t steel", None),
        ("High-temperature heat: electric", "IHT_ELC", "IHT_FOS", "IHT", "EUR/MWh", None),
        ("High-temperature heat: biomethane", "IHT_FOS*", "IHT_FOS", "IHT", "EUR/MWh", {"NG": "BMG"}),
        ("High-temperature heat: hydrogen", "IHT_H2", "IHT_FOS", "IHT", "EUR/MWh", None),
        ("Industrial heat: electrification", "IND_ELC", "IND_FOS", "IND", "EUR/MWh", None),
        ("Industrial heat: fossil gas with CCS", "IND_FCS", "IND_FOS", "IND", "EUR/MWh", None),
        ("Heavy road: biomethane", "RD_BMG", "RD_OIL", "DSL", "EUR/MWh", None),
        ("Aviation: e-kerosene (biogenic CO2)", "EF_EKER", "AV_OIL", None, "EUR/MWh", None),
        ("Bio-CCS at CHP", "CHP_BCS", "CHP_BIO", "ELC", "EUR/MWh el", None),
    ]
    rows = []
    for label, opt, ref, main, unit, swap in cases:
        if opt == "EF_EKER":
            # captured CO2 for e-kerosene priced at the liquefaction route from upgrading
            pr = dict(price, CO2_CAP=LIQ + 0.12 * price["ELC"])
            c_o, e_o = levelised("EF_EKER", "SYN_JET", pr, proc, flows)
            c_o += 0.30 * pr["CO2_CAP"] - 0.30 * STORE  # input CO2 is bought, not stored
            e_o = 0.0
            c_r, e_r = FUEL["OIL_JET"], EF["OIL_JET"]
        else:
            c_o, e_o = levelised(opt.rstrip("*"), main, price, proc, flows, swap)
            if swap:
                c_o += 2.0 * 1.111  # injection cost per MWh of gas used
                e_o = 0.0
            c_r, e_r = levelised(ref, main, price, proc, flows)
        avoided = e_r - e_o
        rows.append({"option": label, "unit": unit, "cost": c_o, "reference cost": c_r,
                     "CO2 avoided (t per unit)": avoided,
                     "cost of avoided CO2 (EUR/t)": (c_o - c_r) / avoided if avoided > 0 else float("nan")})
    rows.append({"option": "Biogenic CO2 from upgrading, stored", "unit": "EUR/t CO2",
                 "cost": LIQ + 0.12 * price["ELC"] + STORE, "reference cost": 0.0,
                 "CO2 avoided (t per unit)": 1.0,
                 "cost of avoided CO2 (EUR/t)": LIQ + 0.12 * price["ELC"] + STORE})
    df = pd.DataFrame(rows)
    df.loc[df.unit == "EUR/t steel", ["cost", "reference cost"]] *= 1  # MEUR/Mt = EUR/t
    return df.sort_values("cost of avoided CO2 (EUR/t)"), price


# ---------------------------------------------------------------- output
def fmt(v, nd=1):
    return "" if pd.isna(v) else f"{v:,.{nd}f}"


def md_table(df, cols, nd):
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        out.append("| " + " | ".join(fmt(r[c], nd.get(c, 1)) if not isinstance(r[c], str) else r[c]
                                      for c in cols) + " |")
    return out


def write(storage, mac, bioc, abat, price):
    L = ["# Hydrogen, biomethane and industrial decarbonisation (v0.2, illustrative data)", "",
         "## 1. Value of hydrogen storage (on time, 2045)", "",
         "Hydrogen is balanced by season; a lined rock cavern store moves it between seasons. "
         "Value of storage = system cost without a store minus system cost with it.", ""]
    L += md_table(storage, list(storage.columns), {"value of storage (MEUR NPV)": 0, "store (TWh)": 2,
                                                   "max level (TWh)": 2, "electrolysis (GW)": 2,
                                                   "electrolysis without store (GW)": 2,
                                                   "store at x0.25 cost (TWh)": 2, "store at x0.1 cost (TWh)": 2,
                                                   "value at x0.25 cost (MEUR NPV)": 0,
                                                   "value at x0.1 cost (MEUR NPV)": 0})
    L += ["", f"## 2. Abatement cost curve: CO2 price mode, {YEAR}", "",
          "CO2 price on gross fossil CO2 rising from 80 EUR/t in 2030 to the stated 2045 level "
          "(no cap, no net-zero constraint). NEGCR = 1: stored biogenic CO2 earns the price.", ""]
    for (s, neg), g in mac.groupby(["scenario", "NEGCR"], sort=False):
        L += [f"### {SCN_LABEL[s]}, stored CO2 {'paid' if neg else 'not paid'}", ""]
        cols = ["price", "gross fossil CO2", "stored CO2", "net CO2", "IHT_FOS", "IHT_ELC", "IHT_H2",
                "BG_AD", "BG_SNG", "GAS_BMG", "RD_BMG", "H2", "H2 store"]
        L += md_table(g, cols, {"price": 0, "H2 store": 2})
        L += [""]
    L += ["IHT_*: high-temperature heat by process (TWh); IHT_FOS burns grid gas, which includes "
          "injected biomethane (GAS_BMG, negative = use). BG_*: biomethane production (TWh). "
          "RD_BMG: biomethane to heavy road transport.", "",
          "## 3. Biogenic carbon debt on additional forest biomass (cap mode, on time, 2045)", ""]
    L += md_table(bioc, list(bioc.columns), {"carbon debt share": 1, "extra cost (MEUR NPV)": 0,
                                             "CO2 price (EUR/t)": 0})
    L += ["", f"## 4. Cost of avoided CO2 by technology at {YEAR} shadow prices (Forest first, on time)", "",
          "Prices used (EUR/MWh): " + ", ".join(f"{k} {v:.0f}" for k, v in price.items()) +
          f"; CO2 storage {STORE:.0f} EUR/t. Levelised capital at 4%.", ""]
    L += md_table(abat, list(abat.columns), {"CO2 avoided (t per unit)": 3,
                                             "cost of avoided CO2 (EUR/t)": 0, "cost": 1,
                                             "reference cost": 1})
    (TAB / "hydrogen_biomethane.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def plot(mac, storage, abat):
    fig, ax = plt.subplots(1, 3, figsize=(12, 3.8))
    lab = {("forest_first", 1): "Forest first", ("forest_first", 0): "Forest first, storage not paid",
           ("electrons_win", 1): "Electrons win"}
    for i, ((s, neg), g) in enumerate(mac.groupby(["scenario", "NEGCR"], sort=False)):
        ax[0].plot(g.price, g["gross fossil CO2"], color=PAL[i], marker="o", ms=3, label=lab[(s, neg)])
        ax[0].plot(g.price, g["net CO2"], color=PAL[i], ls="--", lw=1)
    ax[0].axhline(0, color=INK2, lw=0.6)
    ax[0].set(title=f"Gross (solid) and net (dashed) CO2, {YEAR}", xlabel="CO2 price in 2045 (EUR/t)",
              ylabel="Mt CO2")
    ax[0].legend(fontsize=7)
    g = mac[(mac.scenario == "forest_first") & (mac.NEGCR == 1)]
    ax[1].stackplot(g.price, g.IHT_FOS, g.IHT_ELC, g.IHT_H2, colors=PAL[:3],
                    labels=["Grid gas (fossil or biomethane)", "Electric", "Hydrogen"])
    ax[1].set(title="High-temperature industrial heat, Forest first", xlabel="CO2 price in 2045 (EUR/t)",
              ylabel="TWh")
    ax[1].legend(fontsize=7, loc="lower left")
    ax[2].stackplot(g.price, g.BG_AD, g.BG_SNG, colors=[PAL[2], PAL[3]],
                    labels=["Digestion", "Gasification (bio-SNG)"])
    ax[2].plot(g.price, -g.RD_BMG, color=INK2, lw=1.2, label="of which heavy road")
    ax[2].set(title="Biomethane production, Forest first", xlabel="CO2 price in 2045 (EUR/t)", ylabel="TWh")
    ax[2].legend(fontsize=7, loc="upper left")
    fig.tight_layout()
    fig.savefig(FIG / "fig7_abatement_curve.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
    uses = {"STL_H2": "Steel (DRI)", "EF_EKER": "E-kerosene", "IHT_H2": "High-temperature heat",
            "GT_H2": "Gas turbines"}
    runs = [(SCN_LABEL[s], core(f"{s}_ontime")) for s in SCN]
    bottom = [0.0] * len(runs)
    for i, (p_, l_) in enumerate(uses.items()):
        v = [val(d, "REP_H2", p_, "PRC") for _, d in runs]
        ax[0].bar([r for r, _ in runs], v, bottom=bottom, color=PAL[i], label=l_)
        bottom = [b + x for b, x in zip(bottom, v)]
    ax[0].set(title=f"Hydrogen use in {YEAR} (cap mode, on time)", ylabel="TWh")
    ax[0].legend(fontsize=7)
    mult = [1.0, 0.25, 0.1]
    for i, (_, r) in enumerate(storage.iterrows()):
        size = [r["store (TWh)"], r["store at x0.25 cost (TWh)"], r["store at x0.1 cost (TWh)"]]
        value = [r["value of storage (MEUR NPV)"], r["value at x0.25 cost (MEUR NPV)"],
                 r["value at x0.1 cost (MEUR NPV)"]]
        x = [1.2 * m for m in mult]
        ax[1].plot(x, size, marker="o", color=PAL[i], label=r.scenario)
        for xx, s_, v_ in zip(x, size, value):
            ax[1].annotate(f"{v_:,.0f}", (xx, s_), textcoords="offset points", xytext=(4, 4),
                           fontsize=7, color=PAL[i])
    ax[1].set_xscale("log")
    ax[1].set_xticks([0.12, 0.3, 1.2], ["0.12", "0.3", "1.2"])
    ax[1].set(title=f"Seasonal hydrogen store in {YEAR} vs its cost\n(labels: value of storage, MEUR NPV)",
              xlabel="storage investment cost (EUR per kWh H2)", ylabel="TWh")
    ax[1].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(FIG / "fig8_hydrogen.png", dpi=150)
    plt.close(fig)

    a = abat.dropna(subset=["cost of avoided CO2 (EUR/t)"]).iloc[::-1]
    fig, ax = plt.subplots(figsize=(7, 3.8))
    ax.barh(a.option, a["cost of avoided CO2 (EUR/t)"], color=PAL[0])
    for y, v in enumerate(a["cost of avoided CO2 (EUR/t)"]):
        ax.text(v + 5 if v >= 0 else 5, y, f"{v:,.0f}", va="center", fontsize=7, color=INK2)
    ax.axvline(0, color=INK2, lw=0.6)
    ax.set(title=f"Cost of avoided CO2 at {YEAR} model prices (Forest first)", xlabel="EUR per t CO2")
    fig.tight_layout()
    fig.savefig(FIG / "fig9_cost_of_avoided_co2.png", dpi=150)
    plt.close(fig)


def main():
    (OUT / "gdx").mkdir(parents=True, exist_ok=True)
    storage = storage_runs()
    mac = mac_runs()
    bioc = bioc_runs()
    abat, price = abatement_table()
    for n, df in (("h2_storage", storage), ("mac", mac), ("biogenic_carbon", bioc), ("abatement_cost", abat)):
        df.to_csv(OUT / f"{n}.csv", index=False)
    write(storage, mac, bioc, abat, price)
    plot(mac, storage, abat)
    print((TAB / "hydrogen_biomethane.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
