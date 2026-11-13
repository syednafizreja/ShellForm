"""scripts/day17_verification.py

Run the verification add-ons V1-V5 of the check window (14 Nov 2026) and
write their record files to ``results/``.

None of these runs changes a frozen setting or a frozen result file. Each
output names the ShellBench tag it used. The design inputs (E, nu, loads,
factors) come from ShellBench at the pinned tag through shellform.inputs and
shellform.carbon; the sized thicknesses come from the frozen record
``results/batch_all.csv`` (freeze tag freeze-2026-11-09).

Run from the repository root:

    python scripts/day17_verification.py              # V1-V5
    python scripts/day17_verification.py --only v3 v5 # a subset
    python scripts/day17_verification.py --workers 4

Outputs:

- ``results/verify_v1_zoelly.csv``      sphere benchmark, mesh series, R/t 50 and 100
- ``results/verify_v2_hconv.csv``       8 designs x 4 networks at the sized thickness
- ``results/verify_v3_fdm_residual.csv`` residual of every form-finding solve
- ``results/verify_v4_energy.csv``      membrane energy share of all 168 sized designs
- ``results/verify_v5_formwork.csv``    formwork bound per comparison cell
- ``results/verify_meta.json``          tag, CalculiX version, commands, pass flags
"""

import argparse
import csv
import json
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from shellform.design_space import RISE_RATIOS, SA_LEVELS_G, SPANS_M, SUPPORTS, design_space  # noqa: E402
from shellform.fe import find_ccx  # noqa: E402
from shellform.inputs import load_inputs  # noqa: E402
from shellform.pin import SHELLBENCH_TAG  # noqa: E402
from shellform.pipeline import MEANINGFUL_DIFFERENCE  # noqa: E402
from shellform import verification as V  # noqa: E402

RESULTS = ROOT / "results"
FREEZE_TAG = "freeze-2026-11-09"
BASELINE = RESULTS / "batch_all.csv"
#: V1 meshes (elements per cube-face edge) and radius-to-thickness ratios.
V1_MESHES = (8, 12, 16, 20, 24)
V1_RADIUS_M = 5.0
V1_THICKNESS_M = (0.10, 0.05)  # R/t = 50 and 100
#: V2 designs: both spans and supports, middle rise, gravity form at Sa = 0
#: and seismic-aware form at the largest Sa [J].
V2_RISE = 0.15


def baseline():
    """Return {design_id: row} of the frozen record, checking its tag."""
    with open(BASELINE, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    tags = {r["shellbench_tag"] for r in rows}
    if tags != {SHELLBENCH_TAG}:
        raise ValueError(f"batch_all.csv tags {tags} differ from the pin {SHELLBENCH_TAG}")
    return {r["design_id"]: r for r in rows}


def write(rows, name):
    """Write rows (dicts with the same keys) to results/<name>, tag column first."""
    rows = [dict(shellbench_tag=SHELLBENCH_TAG, **r) for r in rows]
    with open(RESULTS / name, "w", newline="", encoding="utf-8") as fh:
        keys = list(dict.fromkeys(k for r in rows for k in r))
        w = csv.DictWriter(fh, fieldnames=keys, restval="")
        w.writeheader()
        w.writerows(rows)


def _v1(args):
    """Worker: one V1 run."""
    t, m = args
    inp = load_inputs()
    return V.zoelly_benchmark(inp.e_pa, inp.nu, radius_m=V1_RADIUS_M, thickness_m=t, m=m)


def run_v1(workers):
    """V1: sphere benchmark on five meshes at two R/t; returns (rows, summary)."""
    jobs = [(t, m) for t in V1_THICKNESS_M for m in V1_MESHES]
    with ProcessPoolExecutor(workers) as ex:
        rows = list(ex.map(_v1, jobs))
    finest = [r for r in rows if r["m"] == max(V1_MESHES)]
    summary = {"finest_mesh_errors": {f"R/t={r['r_over_t']:.0f}": r["relative_error"] for r in finest},
               "passed": all(r["passed"] for r in finest), "tolerance": V.ZOELLY_TOLERANCE}
    return rows, summary


def v2_cases():
    """Return the eight V2 design cases."""
    want = []
    for span in SPANS_M:
        for sup in SUPPORTS:
            want.append(dict(span_m=span, supports=sup, rise_ratio=V2_RISE, strategy="gravity", sa_g=0.0))
            want.append(dict(span_m=span, supports=sup, rise_ratio=V2_RISE, strategy="seismic", sa_g=max(SA_LEVELS_G)))
    ids = {(c["span_m"], c["supports"], c["rise_ratio"], c["strategy"], c["sa_g"]) for c in want}
    return [c for c in design_space() if (c["span_m"], c["supports"], c["rise_ratio"], c["strategy"], c["sa_g"]) in ids]


def _v2(args):
    """Worker: one V2 point."""
    case, t, n = args
    return dict(design_id=case["design_id"], thickness_m=t, **V.h_point(case, t, n, load_inputs()))


def run_v2(workers, base):
    """V2: h-convergence; returns (rows, summary)."""
    cases = v2_cases()
    jobs = [(c, float(base[c["design_id"]]["thickness_m"]), n) for c in cases for n in V.H_GRIDS]
    with ProcessPoolExecutor(workers) as ex:
        rows = list(ex.map(_v2, jobs))
    fine, finer = V.H_GRIDS[-2], V.H_GRIDS[-1]
    worst = {"buckling_factor": 0.0, "sls_deflection_m": 0.0}
    for c in cases:
        by = {r["n"]: r for r in rows if r["design_id"] == c["design_id"]}
        for r in by.values():
            for k in worst:
                r[f"{k}_change_from_n41"] = r[k] / by[41][k] - 1
        for k in worst:
            ch = abs(by[finer][k] / by[fine][k] - 1)
            by[finer][f"{k}_change_from_previous"] = ch
            worst[k] = max(worst[k], ch)
        # The frozen record must be reproduced on the 41 x 41 network.
        assert abs(by[41]["buckling_factor"] / float(base[c["design_id"]]["buckling_factor"]) - 1) < 1e-6
    by_sup = {}
    for sup in SUPPORTS:
        sel = [r for r in rows if r["n"] == finer and f"-{sup}-" in r["design_id"]]
        by_sup[sup] = {k: max(r[f"{k}_change_from_previous"] for r in sel) for k in worst}
    # The record's 41 x 41 value against the finest network, per support case.
    rec = {sup: [min(r["buckling_factor_change_from_n41"] for r in rows if r["n"] == finer and f"-{sup}-" in r["design_id"]),
                 max(r["buckling_factor_change_from_n41"] for r in rows if r["n"] == finer and f"-{sup}-" in r["design_id"])]
           for sup in SUPPORTS}
    summary = {"finest_pair": [fine, finer], "worst_change_finest_pair": worst,
               "worst_change_finest_pair_by_supports": by_sup,
               "lambda_finest_vs_record_by_supports": rec,
               "passed_buckling": worst["buckling_factor"] < V.H_TOLERANCE,
               "passed_deflection": worst["sls_deflection_m"] < V.H_TOLERANCE,
               "largest_deflection_ratio_finest": max(r["deflection_ratio"] for r in rows if r["n"] == finer),
               "tolerance": V.H_TOLERANCE}
    return rows, summary


def run_v3():
    """V3: FDM residual of all 12 gravity networks, and with the lateral load at every Sa."""
    rows = []
    for span in SPANS_M:
        for sup in SUPPORTS:
            for rise in RISE_RATIOS:
                case = dict(span_m=span, supports=sup, rise_ratio=rise)
                for sa in SA_LEVELS_G:
                    res, pmax = V.fdm_residual_of_case(case, sa_g=sa)
                    rows.append(dict(span_m=span, supports=sup, rise_ratio=rise, sa_g=sa,
                                     residual_inf_n=res, max_nodal_load_n=pmax,
                                     passed=res < V.FDM_RESIDUAL_TOLERANCE))
    worst = max(r["residual_inf_n"] for r in rows)
    return rows, {"networks": len(rows), "worst_residual_n": worst, "tolerance_n": V.FDM_RESIDUAL_TOLERANCE,
                  "passed": all(r["passed"] for r in rows)}


def _v4(args):
    """Worker: one V4 design."""
    case, t = args
    return V.energy_row(case, t, load_inputs())


def run_v4(workers, base):
    """V4: membrane energy share of every sized design."""
    jobs = [(c, float(base[c["design_id"]]["thickness_m"])) for c in design_space()]
    with ProcessPoolExecutor(workers) as ex:
        rows = list(ex.map(_v4, jobs))
    g = np.array([r["membrane_share_uls_gravity"] for r in rows])
    s = np.array([r["membrane_share_uls_seismic_px"] for r in rows if "membrane_share_uls_seismic_px" in r])
    return rows, {"gravity_case_range": [float(g.min()), float(g.max())],
                  "seismic_case_range": [float(s.min()), float(s.max())]}


def run_v5(base):
    """V5: the formwork bound for every comparison cell (Sa > 0 and Sa = 0)."""
    rows = []
    for span in SPANS_M:
        for sup in SUPPORTS:
            for rise in RISE_RATIOS:
                for sa in SA_LEVELS_G:
                    key = lambda st: f"L{span:g}-{sup}-r{rise:.2f}-{st}-sa{sa:.1f}"  # noqa: E731
                    g, s = base[key("gravity")], base[key("seismic")]
                    cg, cs = float(g["carbon_gbt51366_kgco2e_m2"]), float(s["carbon_gbt51366_kgco2e_m2"])
                    ag = float(g["surface_area_m2"]) / float(g["plan_area_m2"])
                    as_ = float(s["surface_area_m2"]) / float(s["plan_area_m2"])
                    rel_c, rel_a = cs / cg - 1, as_ / ag - 1
                    bound = V.formwork_bound(rel_c, rel_a)
                    rows.append(dict(span_m=span, supports=sup, rise_ratio=rise, sa_g=sa,
                                     carbon_gravity_kgco2e_m2=cg, carbon_seismic_kgco2e_m2=cs,
                                     formwork_area_ratio_gravity=ag, formwork_area_ratio_seismic=as_,
                                     rel_carbon=rel_c, rel_formwork_area=rel_a, bound_any_phi=bound,
                                     verdict_safe_for_any_formwork=bound < MEANINGFUL_DIFFERENCE))
    return rows, {"cells": len(rows), "worst_rel_formwork_area": max(abs(r["rel_formwork_area"]) for r in rows),
                  "worst_bound": max(r["bound_any_phi"] for r in rows),
                  "cells_safe": sum(r["verdict_safe_for_any_formwork"] for r in rows)}


def main(argv=None):
    """Run the chosen add-ons and write the record files."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[2])
    ap.add_argument("--only", nargs="*", default=["v1", "v2", "v3", "v4", "v5"])
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args(argv)
    base = baseline()
    meta_path = RESULTS / "verify_meta.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    ccx = find_ccx()
    meta.update(shellbench_tag=SHELLBENCH_TAG, record=f"results/batch_all.csv ({FREEZE_TAG})",
                calculix=subprocess.run([ccx, "-v"], capture_output=True, text=True).stdout.strip() if ccx else None,
                script="scripts/day17_verification.py")
    runs = {"v1": lambda: run_v1(a.workers), "v2": lambda: run_v2(a.workers, base), "v3": run_v3,
            "v4": lambda: run_v4(a.workers, base), "v5": lambda: run_v5(base)}
    names = {"v1": "verify_v1_zoelly.csv", "v2": "verify_v2_hconv.csv", "v3": "verify_v3_fdm_residual.csv",
             "v4": "verify_v4_energy.csv", "v5": "verify_v5_formwork.csv"}
    for key in a.only:
        t0 = time.perf_counter()
        rows, summary = runs[key]()
        write(rows, names[key])
        meta[key] = dict(summary, file=f"results/{names[key]}", wall_time_s=time.perf_counter() - t0)
        print(key, json.dumps(summary, default=float))
    meta_path.write_text(json.dumps(meta, indent=1, default=float) + "\n")


if __name__ == "__main__":
    main()
