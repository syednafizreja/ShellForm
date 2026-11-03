"""scripts/day06_all_designs.py — Day 6: size, take off and compare all 168 designs.

For each design of the full space (10 m and 20 m spans): form-find, size the
thickness (pre-registration section 5), rerun the ULS cases at the sized
thickness for steel, support zones and carbon (D5-1 to D5-5), and apply the
decision rules of section 7. Uses shellform.pipeline, which adds D6-1
(per m2 of covered plan area) and D6-2 (T1 mass on the covered plan area).

Writes:
- results/day06_designs.csv: one row per design (168).
- results/day06_comparison.csv: one row per (span, supports, rise, Sa) (84).
- results/day06_tried.json: every thickness tried, with its checks.
- results/day06_meta.json: ShellBench tag, inputs, factors and status.

Provisional: the carbon factors in ShellBench are still "author to
confirm", and the paper's results come from one run after the 10 Nov
freeze (pre-registration section 9).

Usage: python scripts/day06_all_designs.py [--workers 4] [--spans 10 20]
"""

import argparse
import csv
import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from shellform.carbon import FACTOR_BAND, load_factors
from shellform.design_space import RESULT_COLUMNS, SPANS_M, design_space
from shellform.designs import CORNER_EDGE_INSET_RATIO, N_GRID
from shellform.inputs import load_inputs, shellbench_root
from shellform.pin import SHELLBENCH_TAG, check_pin
from shellform.pipeline import comparison, headline, size_one, take_off_one
from shellform.steel import rho_min

ROOT = Path(__file__).resolve().parents[1]


def run_one(case):
    """Size one design and, if feasible, take off its steel and carbon."""
    row, tried = size_one(case)
    if row["feasible"]:
        row.update(take_off_one(case, row["thickness_m"]))
    return row, tried


def write_csv(rows, path):
    """Write rows to a CSV file; columns are the union of keys, in first-seen order."""
    cols = []
    for r in rows:
        cols += [k for k in r if k not in cols]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, restval="")
        w.writeheader()
        w.writerows(rows)


def main():
    """Run every design of the chosen spans and write the results files."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--spans", type=float, nargs="+", default=list(SPANS_M))
    args = ap.parse_args()
    check_pin()
    cases = design_space(spans=tuple(args.spans))
    with ProcessPoolExecutor(args.workers) as ex:
        out = list(ex.map(run_one, cases))
    rows = [r for r, _ in out]
    res = ROOT / "results"
    lead = list(RESULT_COLUMNS) + ["surface_area_m2", "plan_area_m2", "compression_zone_mpa"]
    write_csv([{**{k: r.get(k, "") for k in lead}, **r} for r in rows], res / "day06_designs.csv")
    feasible = [r for r in rows if r["feasible"]]
    comp = comparison(feasible)
    write_csv(comp, res / "day06_comparison.csv")
    holds, cells = headline(comp)
    inp = load_inputs()
    meta = {"shellbench_tag": SHELLBENCH_TAG, "grid_n": N_GRID, "corner_edge_inset_ratio": CORNER_EDGE_INSET_RATIO,
            "spans_m": args.spans, "n_designs": len(rows), "n_feasible": len(feasible),
            "inputs": inp.as_dict(),
            "rho_min": rho_min(inp, (shellbench_root() / "docs" / "floor_concept.md").read_text(encoding="utf-8")),
            "factors": load_factors().__dict__, "factor_file": "ShellBench data/carbon_factors.csv at " + SHELLBENCH_TAG,
            "factor_band": FACTOR_BAND, "per_m2_basis": "plan area covered by the shell (D6-1)",
            "headline_claim_holds": holds, "headline_cells_seismic_cheaper": cells,
            "status": "provisional: every factor row in ShellBench's file is marked 'author to confirm'"}
    (res / "day06_meta.json").write_text(json.dumps(meta, indent=1) + "\n")
    tried = {"shellbench_tag": SHELLBENCH_TAG, "tried": [c for _, t in out for c in t]}
    (res / "day06_tried.json").write_text(json.dumps(tried, indent=1) + "\n")
    print(f"wrote {len(rows)} designs, {len(feasible)} feasible; headline holds: {holds}")


if __name__ == "__main__":
    main()
