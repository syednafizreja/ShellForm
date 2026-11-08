"""scripts/day05_steel_carbon_10m.py — Day 5: steel, support zones and carbon of the 84 10 m designs.

For each design in results/day04_sizing_10m.csv: rebuild the form, rerun
every ULS load case at the sized thickness, take off the reinforcement and
the thickened support-zone concrete (shellform.steel, decisions D5-1 to
D5-5), and compute A1-A3 carbon with ShellBench's factors and the +/-25 %
band (shellform.carbon, decision P3).

Writes:
- results/day05_steel_carbon_10m.csv: one row per design.
- results/day05_comparison_10m.csv: the two decision rules of
  pre-registration section 7 (cost of resilience; which strategy is cheaper,
  with the 5 % rule), at the central factors and at the four band corners.
- results/day05_meta.json: ShellBench tag, inputs, factors and their status.

These results are provisional: the carbon factors in ShellBench's file are
still marked "author to confirm", and the paper's results come from one run
after the 10 Nov freeze (pre-registration section 9).

Usage: python scripts/day05_steel_carbon_10m.py [--workers 4] [--span 20]

With --span 20 it reads results/day04_sizing_20m.csv and writes the same
files with "20m" in place of "10m" (and results/day05_meta_20m.json). The
file keeps its Day 5 name; Day 6 runs it with --span 20. Since Day 8 the
per-design steps live in shellform.pipeline (same code, moved).
"""

import argparse
import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from shellform.carbon import FACTOR_BAND, factor_status, load_factors
from shellform.design_space import design_space
from shellform.designs import N_GRID
from shellform.inputs import load_inputs, shellbench_root
from shellform.pin import SHELLBENCH_TAG, check_pin
from shellform.pipeline import comparison, sized_thickness, write_csv
from shellform.pipeline import takeoff_one as run_one  # moved to shellform.pipeline on 5 Nov (Day 8)
from shellform.steel import rho_min

ROOT = Path(__file__).resolve().parents[1]


def main():
    """Take off steel and carbon of the sized designs of one span and write the results files."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--span", type=float, default=10.0, help="span [m], one of design_space.SPANS_M")
    args = ap.parse_args()
    check_pin()
    tag = f"{args.span:g}m"
    t = sized_thickness(tag)
    cases = [(c, t[c["design_id"]]) for c in design_space(spans=(args.span,)) if c["design_id"] in t]
    with ProcessPoolExecutor(args.workers) as ex:
        rows = list(ex.map(run_one, cases))
    res = ROOT / "results"
    write_csv(rows, res / f"day05_steel_carbon_{tag}.csv")
    write_csv(comparison(rows), res / f"day05_comparison_{tag}.csv")
    fac = load_factors()
    inp = load_inputs()
    meta = {"shellbench_tag": SHELLBENCH_TAG, "grid_n": N_GRID, "inputs": inp.as_dict(),
            "rho_min": rho_min(inp, (shellbench_root() / "docs" / "floor_concept.md").read_text(encoding="utf-8")),
            "rho_min_source": "ShellBench docs/floor_concept.md, GB 50010 Table 8.5.1 note 2 (slab rule applied to the shell [J])",
            "factors": fac.__dict__, "factor_file": "ShellBench data/carbon_factors.csv at " + SHELLBENCH_TAG,
            "factor_band": FACTOR_BAND,
            "status": factor_status()}
    meta_name = "day05_meta.json" if tag == "10m" else f"day05_meta_{tag}.json"
    (res / meta_name).write_text(json.dumps(meta, indent=1) + "\n")
    print(f"wrote {len(rows)} designs")


if __name__ == "__main__":
    main()
