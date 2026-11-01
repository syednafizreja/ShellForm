"""scripts/day04_mesh_check.py — Day 4 mesh check, 21, 41 and 61 nodes per side.

Baseline shell (10 m span, rise/span 0.15, 80 mm trial thickness) on both
supports, for the gravity form at Sa = 0 and the seismic form at Sa = 0.3 g.
Section 3 of the pre-registration fixes 41 for the design runs and 61 for the
sensitivity check. Writes results/day04_mesh_check.json.

The 80 mm thickness is a trial value for the mesh check, not a sized design.
"""

import json
import os
from concurrent.futures import ProcessPoolExecutor
from itertools import product
from pathlib import Path

os.environ["OMP_NUM_THREADS"] = "1"

from shellform.formfind import corner_network_for_inset, form_to_rise, square_network  # noqa: E402
from shellform.pin import SHELLBENCH_TAG, check_pin  # noqa: E402
from shellform.sb_inputs import load_inputs  # noqa: E402
from shellform.sizing import check_thickness  # noqa: E402
from shellform.strategies import seismic_mid_surface  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SPAN_M, RISE_RATIO, THICKNESS_M, SA_G = 10.0, 0.15, 0.08, 0.3
GRIDS = (21, 41, 61)
CORNER_EDGE_INSET_RATIO = 0.10  # [J] decision D3-1


def one_case(case):
    """Run one grid, support and form; return a result row.

    Args:
        case: (grid n, supports, strategy).
    """
    n, supports, strategy = case
    rise = RISE_RATIO * SPAN_M
    if supports == "edges":
        net = square_network(SPAN_M, n, "edges")
        grav = form_to_rise(net, rise)
    else:
        net, grav, _ = corner_network_for_inset(SPAN_M, n, rise, CORNER_EDGE_INSET_RATIO)
    sa = SA_G if strategy == "seismic" else 0.0
    xyz = seismic_mid_surface(grav, sa, rise) if sa else grav
    r = check_thickness(xyz, n, net.fixed, THICKNESS_M, sa, load_inputs())
    return {"grid_n": n, "supports": supports, "strategy": strategy, "sa_g": sa,
            "lambda_gravity": r.lambda_gravity,
            "lambda_seismic": None if sa == 0.0 else r.lambda_seismic,
            "max_deflection_m": r.max_deflection_m, "period_1_s": r.period_1_s}


def main():
    """Run every case and write the results file."""
    check_pin()
    cases = list(product(GRIDS, ("edges", "corners"), ("gravity", "seismic")))
    with ProcessPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(one_case, cases))
    out = {"shellbench_tag": SHELLBENCH_TAG,
           "inputs": {"span_m": SPAN_M, "rise_ratio": RISE_RATIO, "thickness_m": THICKNESS_M,
                      "sa_g_seismic_form": SA_G, "note": "trial thickness, not a sized design"},
           "rows": rows}
    path = ROOT / "results" / "day04_mesh_check.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
