"""scripts/day04_size_10m.py — Day 4: size the 84 designs with a 10 m span.

For each design: form-find (strategy 1 or 2), size the uniform thickness by
the pre-registered rule (shellform.sizing), then run a modal analysis at the
sized thickness for S5. Writes results/day04_sizing_10m.csv and a JSON file
of every thickness tried.

Steel and carbon columns stay empty until the tension and carbon step (Day 5).
Steel and carbon are missing, so these results are provisional and are not
used in the paper; the paper's results come from one
run after the 10 Nov freeze (pre-registration section 9).

Usage: python scripts/day04_size_10m.py [--workers 4]
"""

import argparse
import csv
import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from shellform.design_space import RESULT_COLUMNS, design_space
from shellform.fe import run_case, surface_area
from shellform.formfind import corner_network_for_inset, form_to_rise, square_network
from shellform.inputs import load_inputs
from shellform.pin import SHELLBENCH_TAG, check_pin
from shellform.sizing import check_as_dict, load_cases, size_design
from shellform.strategies import envelope_thickness, seismic_mid_surface

ROOT = Path(__file__).resolve().parents[1]
N_GRID = 41                    # pre-registration section 3 (41 x 41 network)
CORNER_EDGE_INSET_RATIO = 0.10  # decision D3-1 [J]


def form(case):
    """Return (network, gravity form, mid-surface) for one design case."""
    span, rise = case["span_m"], case["rise_ratio"] * case["span_m"]
    if case["supports"] == "corners":
        net, grav, _ = corner_network_for_inset(span, N_GRID, rise, CORNER_EDGE_INSET_RATIO)
    else:
        net = square_network(span, N_GRID, "edges")
        grav = form_to_rise(net, rise)
    mid = grav.copy() if case["strategy"] == "gravity" else seismic_mid_surface(grav, case["sa_g"], rise)
    return net, grav, mid


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
        m_sdl = (inp.sdl_pa + inp.psi_e_roof * inp.live_pa) / inp.g_m_s2 * span ** 2
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
    """Size all 10 m designs and write the results files."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    check_pin()
    cases = design_space(spans=(10.0,))
    with ProcessPoolExecutor(args.workers) as ex:
        out = list(ex.map(run_one, cases))
    cols = list(RESULT_COLUMNS) + ["surface_area_m2", "compression_zone_mpa"]
    res = ROOT / "results"
    with open(res / "day04_sizing_10m.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for row, _ in out:
            w.writerow(row)
    meta = {"shellbench_tag": SHELLBENCH_TAG, "grid_n": N_GRID, "inputs": load_inputs().as_dict(),
            "status": "provisional: steel and carbon not yet computed",
            "tried": [c for _, t in out for c in t]}
    (res / "day04_sizing_10m_tried.json").write_text(json.dumps(meta, indent=1) + "\n")
    print(f"wrote {len(out)} designs")


if __name__ == "__main__":
    main()
