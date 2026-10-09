"""Locate GAMS and read GDX results into pandas.

Works with the GAMS Python API shipped with a GAMS installation
(gams.transfer; for GAMS 45: pip install "gamsapi[transfer]==45.*") or with
the GAMS system bundled in the gamspy_base pip package.
The GAMS system directory is taken from, in this order: the GAMS_SYSDIR
environment variable, the gamspy_base package, the directory of `gams` on PATH.
"""
import os
import shutil
from pathlib import Path

import pandas as pd


def gams_sysdir():
    if os.environ.get("GAMS_SYSDIR"):
        return Path(os.environ["GAMS_SYSDIR"])
    try:
        import gamspy_base

        return Path(gamspy_base.directory)
    except ImportError:
        pass
    exe = shutil.which("gams")
    if exe:
        return Path(exe).resolve().parent
    raise RuntimeError("GAMS not found: set GAMS_SYSDIR to the GAMS system directory")


def gams_exe():
    name = "gams.exe" if os.name == "nt" else "gams"
    return gams_sysdir() / name


def read_gdx(path, names):
    """Return {symbol name: DataFrame with domain columns + 'value'}."""
    import gams.transfer as gt

    c = gt.Container(str(path), system_directory=str(gams_sysdir()))
    out = {}
    for name in names:
        rec = c[name].records
        if rec is None:
            out[name] = pd.DataFrame()
            continue
        rec = rec.copy()
        if "level" in rec.columns:  # variables: keep the level
            rec = rec.drop(columns=[x for x in ("marginal", "lower", "upper", "scale")
                                    if x in rec.columns])
            rec = rec.rename(columns={"level": "value"})
        dims = list(rec.columns[:-1])
        rec.columns = [d.rsplit("_", 1)[0] if d.rsplit("_", 1)[-1].isdigit() else d
                       for d in dims] + ["value"]
        for d in rec.columns[:-1]:
            rec[d] = rec[d].astype(str)
        out[name] = rec
    return out
