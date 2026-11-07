"""Test S5 (plateau check): the first-mode period of every sized design.

File: src/shellform/s5.py

Pre-registration section 8, S5: the first-mode period T1 of every sized design
must be below Tg = 0.35 s (ShellBench B5), so the equivalent static load
Sa x G_E of section 3 sits on or below the plateau of the design spectrum. Any
failure is reported with its real spectral value.

This module reads T1 from the result files (it runs no analysis) and writes:

- ``results/s5_plateau.csv``: one row per design of the baseline run
  (``results/batch_all.csv``), with T1, T1 / Tg, the spectrum branch and the
  spectral shape alpha(T1) / alpha_max from ShellBench's
  ``seismic.alpha_spectrum`` (GB 50011-2010 cl. 5.1.5, Fig. 5.1.5).
- ``results/s5_summary.csv``: per input file, span and support case, the
  number of designs, the T1 range, the number that fail (T1 >= Tg) and the
  number on the rising branch (T1 < 0.1 s).
- ``results/s5_meta.json``: tags, Tg and the command.

The input files are the baseline and the three sensitivity variants of Day 9
(``sens_lam3``, ``sens_lam8``, ``sens_mesh61``), because their thicknesses, and
so their periods, differ from the baseline.

Rising branch [J]: below 0.1 s the spectrum rises from 0.45 alpha_max at T = 0
(Fig. 5.1.5). The pre-registered load uses the plateau value for every design,
so for a design on the rising branch the applied lateral load is larger than
the spectrum gives, by the factor 1 / (alpha(T1) / alpha_max), at most
1 / 0.45 = 2.2. This is conservative for the seismic case and is reported, not
changed: section 3 fixes the load.

Run: ``python -m shellform.s5``. Units: s.
"""

import argparse
import csv
import json
from pathlib import Path

from shellform.pin import SHELLBENCH_TAG, check_pin

ROOT = Path(__file__).resolve().parents[2]
#: Result files whose periods are checked, by label (Day 8 baseline, Day 9 variants).
INPUT_FILES = {"baseline": "batch_all.csv", "lam3": "sens_lam3.csv",
               "lam8": "sens_lam8.csv", "mesh61": "sens_mesh61.csv"}
#: Columns of results/s5_plateau.csv.
PLATEAU_COLUMNS = ("design_id", "shellbench_tag", "span_m", "supports", "rise_ratio", "strategy",
                   "sa_g", "thickness_m", "period_1_s", "tg_s", "t1_over_tg", "branch",
                   "alpha_shape", "s5_pass")


def spectrum_constants():
    """Return (Tg [s], end of the rising branch [s]) from ShellBench.

    Tg is ``shellbench.seismic.TG_ANCHOR_S`` (spec S4, decision B5, GB 50011-2010
    Table 5.1.4-2); the rising branch ends at ``T_PLATEAU_START_S`` (Fig. 5.1.5).
    """
    import shellbench.seismic as sb

    return sb.TG_ANCHOR_S, sb.T_PLATEAU_START_S


def alpha_shape(period_s, tg_s):
    """Return alpha(T) / alpha_max [-] from ShellBench's design spectrum.

    Args:
        period_s: First-mode period T1 [s].
        tg_s: Characteristic period [s].

    Returns:
        The spectral ordinate as a fraction of alpha_max (1.0 on the plateau).
    """
    import shellbench.seismic as sb

    return sb.alpha_spectrum(period_s, 1.0, tg_s)


def branch(period_s, tg_s, plateau_start_s):
    """Return the spectrum branch of a period: 'rising', 'plateau' or 'descending'."""
    if period_s < plateau_start_s:
        return "rising"
    return "plateau" if period_s <= tg_s else "descending"


def read_rows(path):
    """Read a result CSV as a list of dicts."""
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def plateau_rows(rows, tg_s, plateau_start_s):
    """Return one S5 row per feasible design.

    Args:
        rows: Rows of a batch or sensitivity result file.
        tg_s: Characteristic period [s].
        plateau_start_s: End of the rising branch [s].

    Returns:
        List of dicts with the PLATEAU_COLUMNS keys. Pass means T1 < Tg
        (section 8); an infeasible design has no period and is left out.
    """
    out = []
    for r in rows:
        if r.get("feasible") != "True" or r.get("period_1_s", "") == "":
            continue
        t1 = float(r["period_1_s"])
        out.append({"design_id": r["design_id"], "shellbench_tag": r["shellbench_tag"],
                    "span_m": r["span_m"], "supports": r["supports"],
                    "rise_ratio": r["rise_ratio"], "strategy": r["strategy"], "sa_g": r["sa_g"],
                    "thickness_m": r["thickness_m"], "period_1_s": t1, "tg_s": tg_s,
                    "t1_over_tg": t1 / tg_s, "branch": branch(t1, tg_s, plateau_start_s),
                    "alpha_shape": alpha_shape(t1, tg_s), "s5_pass": t1 < tg_s})
    return out


def summary_rows(label, rows, n_input):
    """Return per (span, supports) summary rows of one input file's S5 rows.

    Args:
        label: Input label (baseline, lam3, ...).
        rows: Output of plateau_rows for that file.
        n_input: Number of designs in the file, feasible or not.
    """
    out = []
    keys = sorted({(float(r["span_m"]), r["supports"]) for r in rows})
    for span, sup in keys:
        g = [r for r in rows if float(r["span_m"]) == span and r["supports"] == sup]
        t = [r["period_1_s"] for r in g]
        out.append({"input": label, "file": f"results/{INPUT_FILES[label]}",
                    "shellbench_tag": ";".join(sorted({r["shellbench_tag"] for r in g})),
                    "span_m": span, "supports": sup, "designs": len(g),
                    "designs_in_file": n_input,
                    "t1_min_s": min(t), "t1_max_s": max(t),
                    "t1_over_tg_max": max(r["t1_over_tg"] for r in g),
                    "fail": sum(1 for r in g if not r["s5_pass"]),
                    "rising_branch": sum(1 for r in g if r["branch"] == "rising"),
                    "alpha_shape_min": min(r["alpha_shape"] for r in g)})
    return out


def write_csv(rows, path, cols=None):
    """Write rows to CSV with the given (or first row's) column order."""
    cols = list(cols or rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main(argv=None):
    """Write results/s5_plateau.csv, s5_summary.csv and s5_meta.json; return 1 on any failure."""
    ap = argparse.ArgumentParser(prog="python -m shellform.s5",
                                 description="S5 plateau check from the result files.")
    ap.parse_args(argv)
    check_pin()
    tg, t0 = spectrum_constants()
    res = ROOT / "results"
    summary, used, base = [], {}, None
    for label, name in INPUT_FILES.items():
        path = res / name
        if not path.exists():
            continue
        rows = read_rows(path)
        s5 = plateau_rows(rows, tg, t0)
        if label == "baseline":
            base = s5
        summary += summary_rows(label, s5, len(rows))
        used[label] = f"results/{name}"
    if base is None:
        raise SystemExit("results/batch_all.csv is missing: run python -m shellform.batch --preset all")
    write_csv(base, res / "s5_plateau.csv", PLATEAU_COLUMNS)
    write_csv(summary, res / "s5_summary.csv")
    fails = sum(s["fail"] for s in summary)
    meta = {"shellbench_tag": SHELLBENCH_TAG, "tg_s": tg, "rising_branch_end_s": t0,
            "tg_source": "shellbench.seismic.TG_ANCHOR_S (spec S4, B5; GB 50011-2010 Table 5.1.4-2)",
            "spectrum_source": "shellbench.seismic.alpha_spectrum (GB 50011-2010 cl. 5.1.5, Fig. 5.1.5)",
            "pass_rule": "T1 < Tg (pre-registration section 8, S5)",
            "inputs": used, "failures": fails,
            "command": "python -m shellform.s5"}
    (res / "s5_meta.json").write_text(json.dumps(meta, indent=1) + "\n")
    for s in summary:
        print(f"{s['input']:8s} {s['span_m']:g} m {s['supports']:7s}: T1 {s['t1_min_s']:.3f}-"
              f"{s['t1_max_s']:.3f} s, max T1/Tg {s['t1_over_tg_max']:.2f}, fail {s['fail']}, "
              f"rising {s['rising_branch']}/{s['designs']}")
    print(f"S5: {fails} failures (ShellBench {SHELLBENCH_TAG})")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
