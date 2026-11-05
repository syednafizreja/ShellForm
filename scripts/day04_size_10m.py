"""scripts/day04_size_10m.py — Day 4: size the 84 designs of one span (10 m by default).

For each design: form-find (strategy 1 or 2), size the uniform thickness by
the pre-registered rule (shellform.sizing), then run a modal analysis at the
sized thickness for S5. Writes results/day04_sizing_<span>m.csv and a JSON
file of every thickness tried (results/day04_sizing_<span>m_tried.json).

Steel and carbon columns stay empty until the tension and carbon step (Day 5).
Steel and carbon are missing, so these results are provisional and are not
used in the paper; the paper's results come from one
run after the 10 Nov freeze (pre-registration section 9).

Usage: python scripts/day04_size_10m.py [--workers 4] [--span 20]

The file keeps its Day 4 name; Day 6 runs it with --span 20. Since Day 8 the
per-design step lives in shellform.pipeline.size_one (same code, moved).
"""

import argparse
import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from shellform.design_space import design_space
from shellform.designs import N_GRID
from shellform.inputs import load_inputs
from shellform.pin import SHELLBENCH_TAG, check_pin
from shellform.pipeline import SIZING_COLUMNS
from shellform.pipeline import size_one as run_one  # moved to shellform.pipeline on 5 Nov (Day 8)

ROOT = Path(__file__).resolve().parents[1]


def main():
    """Size all designs of one span and write the results files."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--span", type=float, default=10.0, help="span [m], one of design_space.SPANS_M")
    args = ap.parse_args()
    check_pin()
    cases = design_space(spans=(args.span,))
    tag = f"{args.span:g}m"
    with ProcessPoolExecutor(args.workers) as ex:
        out = list(ex.map(run_one, cases))
    cols = list(SIZING_COLUMNS)
    res = ROOT / "results"
    with open(res / f"day04_sizing_{tag}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for row, _ in out:
            w.writerow(row)
    meta = {"shellbench_tag": SHELLBENCH_TAG, "grid_n": N_GRID, "inputs": load_inputs().as_dict(),
            "status": "provisional: steel and carbon not yet computed",
            "tried": [c for _, t in out for c in t]}
    (res / f"day04_sizing_{tag}_tried.json").write_text(json.dumps(meta, indent=1) + "\n")
    print(f"wrote {len(out)} designs")


if __name__ == "__main__":
    main()
