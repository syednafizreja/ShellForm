"""scripts/day12_freeze.py — Day 12: the freeze run (pre-registration section 9).

One command reruns every result the paper uses, from the frozen code, at the
pinned ShellBench tag (src/shellform/pin.py):

1. ``python -m shellform.batch --preset all --compare-record`` — the baseline,
   all 168 designs, checked against the committed Day 4-6 record.
2. The Day 4-6 record files (``day04_sizing_<span>m.csv``, ``_tried.json``)
   rewritten from step 1, then ``scripts/day05_steel_carbon_10m.py --span``
   10 and 20 (steel, carbon and the strategy comparison) from those
   thicknesses, so that the record and the gallery name the pinned tag.
3. ``python -m shellform.sensitivity --run lam3 lam8 mesh61 --summarise``.
4. ``python -m shellform.s5``, ``python -m shellform.crosscheck`` and
   ``python -m shellform.crosscheck --modes``.
5. ``python scripts/day11_figures.py`` — every paper figure.

It writes ``results/freeze_meta.json``: the freeze tag, the commit the code
ran from, the ShellBench tag, the CalculiX version, and each step's command,
exit status and wall time. It stops at the first step that fails.

Usage (from the repository root, in env ``shellform``, with the working tree
at the freeze tag):

    python scripts/day12_freeze.py [--workers 4] [--from-step 1]
"""

import argparse
import csv
import json
import subprocess
import sys
import time
from pathlib import Path

from shellform.batch import ccx_version
from shellform.designs import N_GRID
from shellform.inputs import load_inputs
from shellform.pin import SHELLBENCH_TAG, check_pin
from shellform.pipeline import SIZING_COLUMNS

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"

#: The git tag of the frozen code (pre-registration section 9, amendment of 9 Nov 2026).
FREEZE_TAG = "freeze-2026-11-09"

#: Spans of the design space with a Day 4-6 record file each [m] (design_space.SPANS_M).
RECORD_SPANS_M = (10.0, 20.0)


def git(*args):
    """Return the stripped output of a git command run in the repository root."""
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def records_from_batch():
    """Rewrite results/day04_sizing_<span>m.csv and _tried.json from results/batch_all.*.

    The batch runs the same shellform.pipeline.size_one as scripts/day04_size_10m.py,
    so the rows are the Day 4 rows (sizing columns only); steel and carbon follow
    from scripts/day05_steel_carbon_10m.py.
    """
    with open(RES / "batch_all.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    meta = json.loads((RES / "batch_all_meta.json").read_text(encoding="utf-8"))
    cols = list(SIZING_COLUMNS)
    for span in RECORD_SPANS_M:
        tag = f"{span:g}m"
        sel = [r for r in rows if float(r["span_m"]) == span]
        ids = {r["design_id"] for r in sel}
        with open(RES / f"day04_sizing_{tag}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(sel)
        tried = {"shellbench_tag": SHELLBENCH_TAG, "grid_n": N_GRID, "inputs": load_inputs().as_dict(),
                 "status": "written from results/batch_all.csv by scripts/day12_freeze.py (freeze run)",
                 "tried": [c for c in meta["tried"] if c["design_id"] in ids]}
        (RES / f"day04_sizing_{tag}_tried.json").write_text(json.dumps(tried, indent=1) + "\n")
        print(f"wrote day04 record for {tag}: {len(sel)} designs")
    return 0


def steps(workers):
    """Return the freeze steps as (name, command list or callable)."""
    py = sys.executable
    w = ["--workers", str(workers)]
    out = [("batch_all", [py, "-m", "shellform.batch", "--preset", "all", "--compare-record", *w]),
           ("day04_records", records_from_batch)]
    out += [(f"day05_{s:g}m", [py, "scripts/day05_steel_carbon_10m.py", "--span", f"{s:g}", *w])
            for s in RECORD_SPANS_M]
    out += [("sensitivity", [py, "-m", "shellform.sensitivity", "--run", "lam3", "lam8", "mesh61",
                             "--summarise", *w]),
            ("s5", [py, "-m", "shellform.s5"]),
            ("crosscheck", [py, "-m", "shellform.crosscheck", *w]),
            ("crosscheck_modes", [py, "-m", "shellform.crosscheck", "--modes", *w]),
            ("figures", [py, "scripts/day11_figures.py"])]
    return out


def main(argv=None):
    """Run the freeze steps in order and write results/freeze_meta.json."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--from-step", type=int, default=1, help="1-based step to start from (resume)")
    a = ap.parse_args(argv)
    check_pin()
    meta_path = RES / "freeze_meta.json"
    meta = (json.loads(meta_path.read_text()) if a.from_step > 1 and meta_path.exists() else
            {"freeze_tag": FREEZE_TAG, "code_commit": git("rev-parse", "HEAD"),
             "code_describe": git("describe", "--tags", "--always"),
             "shellbench_tag": SHELLBENCH_TAG, "calculix": ccx_version(), "grid_n": N_GRID,
             "steps": []})
    for i, (name, cmd) in enumerate(steps(a.workers), start=1):
        if i < a.from_step:
            continue
        print(f"[{i}] {name}", flush=True)
        t0 = time.perf_counter()
        if callable(cmd):
            code, shown = cmd(), f"scripts/day12_freeze.py:{cmd.__name__}"
        else:
            code = subprocess.run(cmd, cwd=ROOT).returncode
            shown = " ".join(["python", *cmd[1:]])
        meta["steps"].append({"step": i, "name": name, "command": shown, "exit": code,
                              "wall_time_s": round(time.perf_counter() - t0, 1)})
        meta_path.write_text(json.dumps(meta, indent=1) + "\n")
        if code != 0:
            raise SystemExit(f"step {i} ({name}) failed with exit status {code}")
    print("freeze run complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
