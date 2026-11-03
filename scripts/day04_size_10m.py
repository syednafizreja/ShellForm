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

The file keeps its Day 4 name; Day 6 runs it with --span 20.
"""

import argparse
import csv
import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from shellform.design_space import RESULT_COLUMNS, design_space
from shellform.designs import N_GRID, form
from shellform.fe import plan_area, run_case, surface_area
from shellform.inputs import load_inputs
from shellform.pin import SHELLBENCH_TAG, check_pin
from shellform.sizing import check_as_dict, load_cases, size_design
from shellform.strategies import envelope_thickness

ROOT = Path(__file__).resolve().parents[1]


def run_one(case):
    """Size one design and return (results row, list of tried checks)."""
    inp = load_inputs()
    net, grav, mid = form(case)
    span, sa = case["span_m"], case["sa_g"]
    best, tried = size_design(mid, N_GRID, net.fixed, span, inp, sa)
    area = surface_area(mid, N_GRID)
    row = {k: "" for k in RESULT_COLUMNS}
    row.update(case)
    row.update(shellbench_tag=SHELLBENCH_TAG, feasible=best is not None,
               t_env_m=envelope_thickness(mid, grav, sa))
    if best is not None:
        _, sls = load_cases(inp, sa)
        modal = run_case(mid, N_GRID, net.fixed, best.thickness_m, inp.e_pa, inp.nu,
                         inp.density_kg_m3, sls[0], sls[1], n_modes=1)
        # FREQUENCY uses the concrete mass only; scale T1 for the SDL mass of G_E [J].
        m_self = inp.density_kg_m3 * best.thickness_m * area
        # SDL and live load act per plan area (D4-5), so their mass uses the plan
        # area of the shell, not span ** 2 (amendment of 3 Nov 2026).
        m_sdl = (inp.sdl_pa + inp.psi_e_roof * inp.live_pa) / inp.g_m_s2 * plan_area(mid, N_GRID)
        row.update(thickness_m=best.thickness_m, concrete_m3=best.thickness_m * area,
                   buckling_factor=best.buckling_factor,
                   period_1_s=float(modal.periods_s[0] * np.sqrt((m_self + m_sdl) / m_self)),
                   max_compression_mpa=best.compression_pa / 1e6,
                   max_deflection_m=best.deflection_m)
    governing = ""
    if tried:
        below = [c for t, c in tried.items() if best is None or t < best.thickness_m]
        governing = max(below, key=lambda c: c.thickness_m).governing if below else "t_min"
    row.update(governing_check=governing, surface_area_m2=area,
               compression_zone_mpa="" if best is None else best.compression_zone_pa / 1e6)
    return row, [dict(design_id=case["design_id"], **check_as_dict(c)) for c in tried.values()]


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
    cols = list(RESULT_COLUMNS) + ["surface_area_m2", "compression_zone_mpa"]
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
