"""Batch runner: run any set of designs, start to finish, from one command.

For each selected design it runs the whole chain in one pass: form-finding,
thickness sizing and the modal analysis (shellform.pipeline.size_one), then
steel, support zones and carbon at the sized thickness
(shellform.pipeline.takeoff_one). The code is the same code that wrote the
Day 4 to Day 6 results; only the order is new (one design at a time, both
steps together).

Every row names the ShellBench tag it used (CLAUDE.md, code standards), and
the meta file names the tag, the CalculiX version and the command.

Usage examples (from the repo root, in env ``shellform``):

    python -m shellform.batch                      # preset "smoke8": 8 designs
    python -m shellform.batch --preset all         # all 168 designs
    python -m shellform.batch --span 10 --supports corners --sa 0.0 0.6
    python -m shellform.batch --ids L10-edges-r0.10-gravity-sa0.0
    python -m shellform.batch --compare-record     # also check against results/

With --compare-record, each row is compared with the committed Day 4 to
Day 6 record (results/day04_sizing_<span>m.csv and
results/day05_steel_carbon_<span>m.csv). Text columns and the thickness
must match exactly; numbers must match to RECORD_REL_TOL. The command exits
with status 1 if any value is outside, so it can be used as a check.

Writes results/batch_<name>.csv and results/batch_<name>_meta.json, with
<name> the preset name or the value of --name. These results are
provisional like the record (carbon factors still "author to confirm"); the
paper's results come from one run after the 10 Nov freeze
(pre-registration section 9).
"""

import argparse
import csv
import json
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from shellform.design_space import SA_LEVELS_G, design_space
from shellform.designs import N_GRID
from shellform.fe import find_ccx
from shellform.pin import SHELLBENCH_TAG, check_pin
from shellform.pipeline import ROOT, SIZING_COLUMNS, size_one, takeoff_one, write_csv

#: Preset selections. "smoke8" [J]: one design per (span, supports, strategy)
#: at the middle rise (0.15) and the Sa of the pre-registered S4 case
#: (0.3 g), so every span, support case and strategy is touched.
PRESETS = {
    "smoke8": dict(rise=(0.15,), sa=(0.3,)),
    "all": dict(),
}

#: Columns compared with the record, and the file each comes from.
RECORD_SIZING_COLUMNS = ("feasible", "thickness_m", "governing_check", "buckling_factor",
                         "period_1_s", "max_compression_mpa", "max_deflection_m", "t_env_m")
RECORD_TAKEOFF_COLUMNS = ("concrete_m3", "steel_kg", "steel_governing_case",
                          "carbon_gbt51366_kgco2e_m2")
#: Columns that must match the record exactly (text, or the sized thickness).
RECORD_EXACT = ("feasible", "thickness_m", "governing_check", "steel_governing_case")
#: Relative tolerance on the other numbers [J]. The record was written with
#: CalculiX 2.23 on the laptop; the cloud has 2.21. On Day 4 the two versions
#: differed by at most 2.3e-4 (deflection), so 1e-3 leaves room for that and
#: still catches any change of model.
RECORD_REL_TOL = 1e-3


def select(preset=None, spans=None, supports=None, rise=None, strategy=None, sa=None, ids=None):
    """Return the design cases picked by a preset and/or filters.

    Args:
        preset: A key of PRESETS, or None for no preset.
        spans, supports, rise, strategy, sa: Sequences of allowed levels, or
            None for all. Filters given here narrow the preset.
        ids: Sequence of design_ids, or None. Unknown ids raise ValueError.

    Returns:
        List of case dicts in design_space order.
    """
    f = dict(PRESETS[preset]) if preset else {}
    for key, val in (("spans", spans), ("supports", supports), ("rise", rise),
                     ("strategy", strategy), ("sa", sa)):
        if val is not None:
            f[key] = tuple(val)
    cases = design_space()
    if ids is not None:
        known = {c["design_id"] for c in cases}
        bad = [i for i in ids if i not in known]
        if bad:
            raise ValueError(f"unknown design_id: {', '.join(bad)}")
        cases = [c for c in cases if c["design_id"] in set(ids)]

    def keep(c):
        return ((f.get("spans") is None or any(abs(c["span_m"] - s) < 1e-9 for s in f["spans"]))
                and (f.get("supports") is None or c["supports"] in f["supports"])
                and (f.get("rise") is None or any(abs(c["rise_ratio"] - r) < 1e-9 for r in f["rise"]))
                and (f.get("strategy") is None or c["strategy"] in f["strategy"])
                and (f.get("sa") is None or any(abs(c["sa_g"] - a) < 1e-9 for a in f["sa"])))

    return [c for c in cases if keep(c)]


def run_design(case):
    """Run one design start to finish.

    Returns:
        (row, tried): row has the SIZING_COLUMNS, overwritten and extended by
        the take-off columns when the design is feasible (concrete_m3 then
        includes the support-zone concrete); tried lists every thickness tried.
    """
    t0 = time.perf_counter()
    row, tried = size_one(case)
    if row["feasible"]:
        row.update(takeoff_one((case, row["thickness_m"])))
    row["runtime_s"] = time.perf_counter() - t0
    return row, tried


def _record_rows(span_tag):
    """Return {design_id: merged record row} from the committed Day 4-6 files of one span."""
    rec = {}
    for name in (f"day04_sizing_{span_tag}.csv", f"day05_steel_carbon_{span_tag}.csv"):
        path = ROOT / "results" / name
        if not path.exists():
            continue
        with open(path, newline="") as fh:
            for r in csv.DictReader(fh):
                rec.setdefault(r["design_id"], {}).update(
                    {k: r[k] for k in r if k in (RECORD_TAKEOFF_COLUMNS if "day05" in name
                                                 else RECORD_SIZING_COLUMNS)})
    return rec


def compare_with_record(rows):
    """Compare batch rows with the committed record.

    Args:
        rows: Rows of run_design.

    Returns:
        (summary dict, list of mismatch dicts). The summary gives, per column,
        the largest relative difference found, and the number of rows that had
        a record row.
    """
    cache, worst, bad, matched = {}, {}, [], 0
    for row in rows:
        tag = f"{row['span_m']:g}m"
        rec = cache.setdefault(tag, _record_rows(tag)).get(row["design_id"])
        if rec is None:
            continue
        matched += 1
        for col, ref in rec.items():
            val = row.get(col, "")
            if col in RECORD_EXACT:
                same = (str(val) == ref if col != "thickness_m"
                        else ref != "" and val != "" and abs(float(val) - float(ref)) < 1e-9)
                if not same:
                    bad.append(dict(design_id=row["design_id"], column=col, batch=val, record=ref))
                continue
            if ref == "" and val == "":
                continue
            ref_f, val_f = float(ref), float(val)
            rel = abs(val_f - ref_f) / max(abs(ref_f), 1e-30)
            worst[col] = max(worst.get(col, 0.0), rel)
            if rel > RECORD_REL_TOL:
                bad.append(dict(design_id=row["design_id"], column=col, batch=val_f, record=ref_f,
                                rel_diff=rel))
    summary = {"rows_with_record": matched, "rel_tol": RECORD_REL_TOL,
               "exact_columns": list(RECORD_EXACT), "max_rel_diff": worst,
               "mismatches": len(bad)}
    return summary, bad


def ccx_version():
    """Return the first line of ``ccx -v``, or "" if CalculiX is not found."""
    ccx = find_ccx()
    if ccx is None:
        return ""
    out = subprocess.run([ccx, "-v"], capture_output=True, text=True, check=False)
    lines = [ln.strip() for ln in (out.stdout + out.stderr).splitlines() if ln.strip()]
    return lines[0] if lines else ""


def parse_args(argv=None):
    """Parse the command line (see the module docstring)."""
    ap = argparse.ArgumentParser(prog="python -m shellform.batch",
                                 description="Run ShellForm designs start to finish.")
    ap.add_argument("--preset", choices=sorted(PRESETS), default=None,
                    help="named selection; default smoke8 when no filter or id is given")
    ap.add_argument("--span", type=float, nargs="+", dest="spans", help="spans [m]")
    ap.add_argument("--supports", nargs="+", choices=("corners", "edges"))
    ap.add_argument("--rise", type=float, nargs="+", help="rise-to-span ratios")
    ap.add_argument("--strategy", nargs="+", choices=("gravity", "seismic"))
    ap.add_argument("--sa", type=float, nargs="+", help=f"Sa levels [g], of {SA_LEVELS_G}")
    ap.add_argument("--ids", nargs="+", help="design_ids")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--name", help="output name; default the preset name, else 'custom'")
    ap.add_argument("--compare-record", action="store_true",
                    help="compare with the committed Day 4-6 results; exit 1 on a mismatch")
    a = ap.parse_args(argv)
    filters = (a.spans, a.supports, a.rise, a.strategy, a.sa, a.ids)
    if a.preset is None and all(v is None for v in filters):
        a.preset = "smoke8"
    a.name = a.name or a.preset or "custom"
    return a


def main(argv=None):
    """Run the selected designs and write results/batch_<name>.csv and its meta file."""
    a = parse_args(argv)
    check_pin()
    cases = select(a.preset, a.spans, a.supports, a.rise, a.strategy, a.sa, a.ids)
    if not cases:
        raise SystemExit("no design matches the selection")
    t0 = time.perf_counter()
    with ProcessPoolExecutor(a.workers) as ex:
        out = list(ex.map(run_design, cases))
    rows = [r for r, _ in out]
    cols = list(SIZING_COLUMNS)
    for r in rows:
        cols += [k for k in r if k not in cols]
    rows = [{k: r.get(k, "") for k in cols} for r in rows]
    res = ROOT / "results"
    write_csv(rows, res / f"batch_{a.name}.csv")
    meta = {"shellbench_tag": SHELLBENCH_TAG, "calculix": ccx_version(), "grid_n": N_GRID,
            "command": "python -m shellform.batch " + " ".join(sys.argv[1:] if argv is None else argv),
            "preset": a.preset, "designs": len(rows),
            "feasible": sum(1 for r in rows if r["feasible"]),
            "wall_time_s": time.perf_counter() - t0,
            "status": "provisional: carbon factors in ShellBench's file are marked 'author to confirm'",
            "tried": [c for _, t in out for c in t]}
    status = 0
    if a.compare_record:
        summary, bad = compare_with_record(rows)
        meta["record_check"] = dict(summary, mismatch_rows=bad)
        status = 1 if bad else 0
        print(f"record check: {summary['rows_with_record']} rows compared, "
              f"{summary['mismatches']} mismatches")
        for col, rel in sorted(summary["max_rel_diff"].items()):
            print(f"  {col}: max relative difference {rel:.2e}")
    (res / f"batch_{a.name}_meta.json").write_text(json.dumps(meta, indent=1) + "\n")
    print(f"wrote {len(rows)} designs to results/batch_{a.name}.csv (ShellBench {SHELLBENCH_TAG})")
    return status


if __name__ == "__main__":
    raise SystemExit(main())
