"""scripts/day04_sizing.py — Day 4 thickness search on the 84 cases of the 10 m span.

Sizes every 10 m case at 41 x 41 nodes against buckling and deflection only
(docs/preregistration.md, amendment of 1 Nov). Compression and tension are not
checked yet, so these thicknesses are lower bounds, not sized designs, and no
carbon is computed. A subset is sized again at 61 x 61 as a mesh check.
Writes results/day04_sizing_10m.csv and results/day04_sizing_10m_grid61.csv.
"""

import csv
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

os.environ["OMP_NUM_THREADS"] = "1"

from shellform.design_space import design_space  # noqa: E402
from shellform.formfind import corner_network_for_inset, form_to_rise, square_network  # noqa: E402
from shellform.pin import SHELLBENCH_TAG, check_pin  # noqa: E402
from shellform.sb_inputs import load_inputs  # noqa: E402
from shellform.sizing import check_thickness, governing_check, size_shell  # noqa: E402
from shellform.strategies import envelope_thickness, seismic_mid_surface  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DESIGN_GRID, CHECK_GRID = 41, 61  # section 3
CORNER_EDGE_INSET_RATIO = 0.10    # [J] decision D3-1
CHECK_RISE_RATIO, CHECK_SA_G = 0.15, (0.0, 0.3, 0.6)  # subset sized at 61 x 61 [J]
COLUMNS = ("design_id", "shellbench_tag", "grid_n", "span_m", "supports", "rise_ratio", "strategy",
           "sa_g", "feasible", "thickness_lower_bound_m", "buckling_factor", "lambda_gravity",
           "lambda_seismic", "lambda_one_step_below", "period_1_s", "max_deflection_m",
           "governing_check", "t_env_m")


def size_case(job):
    """Size one design case and return its result row.

    Args:
        job: (case dict from design_space, grid nodes per side).
    """
    case, n = job
    span, rise = case["span_m"], case["rise_ratio"] * case["span_m"]
    if case["supports"] == "edges":
        net = square_network(span, n, "edges")
        grav = form_to_rise(net, rise)
    else:
        net, grav, _ = corner_network_for_inset(span, n, rise, CORNER_EDGE_INSET_RATIO)
    sa = case["sa_g"]
    xyz = seismic_mid_surface(grav, sa, rise) if case["strategy"] == "seismic" else grav
    inputs = load_inputs()
    feasible, r = size_shell(xyz, n, net.fixed, span, sa, inputs)
    below = None
    if r.thickness_m > 0.05 + 1e-9:
        below = check_thickness(xyz, n, net.fixed, round(r.thickness_m - 0.005, 3), sa,
                                inputs).lambda_governing
    return {"design_id": case["design_id"], "shellbench_tag": SHELLBENCH_TAG, "grid_n": n,
            "span_m": span, "supports": case["supports"], "rise_ratio": case["rise_ratio"],
            "strategy": case["strategy"], "sa_g": sa, "feasible": feasible,
            "thickness_lower_bound_m": r.thickness_m, "buckling_factor": r.lambda_governing,
            "lambda_gravity": r.lambda_gravity, "lambda_seismic": r.lambda_seismic,
            "lambda_one_step_below": below, "period_1_s": r.period_1_s,
            "max_deflection_m": r.max_deflection_m, "governing_check": governing_check(r, span),
            "t_env_m": envelope_thickness(xyz, grav, sa)}


def write_rows(path, rows):
    """Write result rows to a CSV file in the fixed column order."""
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def main():
    """Size all 10 m cases, then the 61 x 61 subset, and write both files."""
    check_pin()
    cases = design_space(spans=(10.0,))
    subset = [c for c in cases if c["supports"] == "corners"
              and c["rise_ratio"] == CHECK_RISE_RATIO and c["sa_g"] in CHECK_SA_G]
    with ProcessPoolExecutor(max_workers=12) as pool:
        rows = list(pool.map(size_case, [(c, DESIGN_GRID) for c in cases]))
        fine = list(pool.map(size_case, [(c, CHECK_GRID) for c in subset]))
    write_rows(ROOT / "results" / "day04_sizing_10m.csv", rows)
    write_rows(ROOT / "results" / "day04_sizing_10m_grid61.csv", fine)
    print(f"{len(rows)} cases at {DESIGN_GRID}, {len(fine)} at {CHECK_GRID}")


if __name__ == "__main__":
    main()
