"""Cross-check of ShellForm's CalculiX deck (fe.py) against ShellBench's shell wrapper.

File: src/shellform/crosscheck.py

Pre-registration, amendment of 31 Oct 2026: ShellForm writes its own S8R deck
(``shellform.fe``) because ShellBench's CalculiX shell wrapper was not tagged.
"When floor-r2 is tagged, both are run on the same shell and the difference is
reported; ShellBench's wrapper is used for the results if they differ by more
than 2 %." ShellBench v0.2.0 (pinned 7 Nov 2026) carries that wrapper as
``shellbench.shellfe`` (ShellBench playbook Day 24: Scordelis-Lo roof and
pinched hemisphere within 2 %). The tag is named v0.2.0, not floor-r2.

What is compared [J]: the gravity form of each span and support case at rise
0.15 (the smoke8 rise, D8-1), at its sized thickness from
``results/batch_all.csv``. Both programs get the same nodes, the same S8R
elements, the same pinned nodes (translations fixed), the same E, nu and
density (``shellform.inputs``, read from ShellBench) and self-weight only.
Two quantities: the largest displacement of the static step and the first
linear buckling factor. Self-weight alone is used because it is the one load
both programs apply the same way (GRAV on all elements); ShellForm's sizing
adds plan-area nodal loads that ShellBench's wrapper has no helper for.

Writes ``results/fe_crosscheck.csv`` and ``results/fe_crosscheck_meta.json``.
Run: ``python -m shellform.crosscheck``. Units: m, N, Pa, kg.

Both programs are compared at the same number of requested buckling factors
(2, as ``fe.analyse`` asks for), because CalculiX's eigensolver returns a
slightly high lowest factor when few are requested (found on 7 Nov 2026).
``--modes`` measures that effect on the sizing: every design of the baseline
and the three Day 9 variants whose recorded buckling factor (1 factor
requested, the record) is within 3 % of its threshold is checked again at its
sized thickness with 4 factors requested, and
``results/buckling_modes_check.csv`` says whether it would still pass.
This measured the files run before D10-1 (7 Nov 2026); since D10-1 the
sizing itself asks for 4 factors (``sizing.N_BUCKLE_SIZING``), so the
committed table is the record of that measurement and ``--modes`` is not
part of the routine run.
"""

import argparse
import csv
import json
import tempfile
from pathlib import Path

import numpy as np

from shellform.designs import form, grid_n
from shellform.fe import analyse, s8r_elements
from shellform.inputs import load_inputs
from shellform.pin import SHELLBENCH_TAG, check_pin

ROOT = Path(__file__).resolve().parents[2]
#: Pass limit from the 31 Oct amendment.
TOLERANCE = 0.02
#: Buckling factors requested in both programs (fe.analyse asks for 2).
COMPARE_BUCKLING_MODES = 2
#: Buckling factors requested in the --modes check; corner shells are
#: converged at 2 (7 Nov 2026), so 4 leaves a margin [J].
CONVERGED_BUCKLING_MODES = 4
#: Designs whose recorded factor is below threshold x (1 + this) are rechecked.
MODES_MARGIN = 0.03
#: Rise of the compared shells (smoke8 rise, D8-1) [J].
CHECK_RISE = 0.15
#: Sa level of the compared rows; the gravity form does not depend on it.
CHECK_SA_G = 0.3


def cases():
    """Return the four compared cases (two spans x two support cases, gravity form)."""
    from shellform.design_space import design_space

    return [c for c in design_space()
            if c["strategy"] == "gravity" and c["rise_ratio"] == CHECK_RISE
            and abs(c["sa_g"] - CHECK_SA_G) < 1e-12]


def sized_thickness(design_id, path=None):
    """Return the sized thickness of one design from results/batch_all.csv [m]."""
    path = path or ROOT / "results" / "batch_all.csv"
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["design_id"] == design_id:
                return float(r["thickness_m"])
    raise KeyError(design_id)


def shellbench_model(xyz, n, fixed, thickness_m, e_pa, nu, density_kg_m3, g):
    """Build ShellBench's ShellModel for the same shell as shellform.fe.write_deck.

    Args:
        xyz: Grid nodes, shape (n*n, 3) [m].
        n: Grid nodes per side (odd).
        fixed: 0-based indices of pinned nodes.
        thickness_m, e_pa, nu, density_kg_m3, g: As for shellform.fe.

    Returns:
        shellbench.shellfe.ShellModel with self-weight as GRAV (0, 0, -1).
    """
    from shellbench.shellfe import ShellModel

    els = s8r_elements(n)
    used = sorted(int(u) for u in np.unique(els))
    nodes = {k: tuple(float(v) for v in xyz[k - 1]) for k in used}
    fixed_used = sorted(set(int(k) + 1 for k in fixed) & set(used))
    return ShellModel(nodes=nodes, elements=[tuple(int(v) for v in e) for e in els],
                      thickness=thickness_m, e=e_pa, nu=nu, density=density_kg_m3,
                      supports=[(k, 1, 3) for k in fixed_used], gravity=(g, 0.0, 0.0, -1.0))


def compare_one(case, thickness_m, workdir):
    """Run one shell in both programs and return the comparison row."""
    from shellbench.shellfe import run as sb_run

    inp = load_inputs()
    net, _, mid = form(case)
    n = grid_n(case)
    args = (mid, n, net.fixed, thickness_m, inp.e_pa, inp.nu, inp.density_kg_m3)
    sf = analyse(*args, g=inp.g_m_s2, workdir=workdir / "shellform")
    model = shellbench_model(*args, g=inp.g_m_s2)
    st = sb_run(model, workdir / "shellbench", "static")
    bk = sb_run(model, workdir / "shellbench", "buckle", buckling_modes=COMPARE_BUCKLING_MODES)
    sb_disp = max(float(np.linalg.norm(u)) for u in st.displacements.values())
    sf_buck = float(sf.buckling_factors[0])
    sb_buck = float(bk.buckling_factors[0])
    d_disp = abs(sf.max_disp_m - sb_disp) / sb_disp
    d_buck = abs(sf_buck - sb_buck) / sb_buck
    return {"design_id": case["design_id"], "shellbench_tag": SHELLBENCH_TAG,
            "span_m": case["span_m"], "supports": case["supports"],
            "rise_ratio": case["rise_ratio"], "thickness_m": thickness_m, "grid_n": n,
            "elements": len(model.elements), "pinned_nodes": len(model.supports),
            "max_disp_shellform_m": sf.max_disp_m, "max_disp_shellbench_m": sb_disp,
            "disp_rel_diff": d_disp,
            "buckling_shellform": sf_buck, "buckling_shellbench": sb_buck,
            "buckling_rel_diff": d_buck,
            "within_tolerance": d_disp <= TOLERANCE and d_buck <= TOLERANCE}


def _recheck(args):
    """Recheck one design at its sized thickness with more buckling factors (worker)."""
    from shellform.sizing import check_thickness

    row, n_buckle, lambda_min = args
    case = {k: row[k] for k in ("design_id", "supports", "strategy")}
    case.update(span_m=float(row["span_m"]), rise_ratio=float(row["rise_ratio"]),
                sa_g=float(row["sa_g"]))
    if row.get("grid_n"):
        case["grid_n"] = int(float(row["grid_n"]))
    net, _, mid = form(case)
    t = float(row["thickness_m"])
    chk = check_thickness(mid, grid_n(case), net.fixed, case["span_m"], t, load_inputs(),
                          case["sa_g"], n_buckle=n_buckle, lambda_min=lambda_min)
    lam1 = float(row["buckling_factor"])
    return {"design_id": row["design_id"], "shellbench_tag": SHELLBENCH_TAG,
            "record_tag": row["shellbench_tag"], "grid_n": grid_n(case),
            "thickness_m": t, "lambda_min": lambda_min, "buckling_1_requested": lam1,
            "buckling_converged": chk.buckling_factor, "buckling_factors_requested": n_buckle,
            "rel_diff": (lam1 - chk.buckling_factor) / chk.buckling_factor,
            "passes_converged": chk.passed, "governing_converged": chk.governing}


#: Files rechecked by mode_check, with the buckling threshold each was sized to
#: (pre-registration sections 5 and 7; Day 9 variants).
MODE_CHECK_FILES = {"baseline": ("batch_all.csv", 5.0), "lam3": ("sens_lam3.csv", 3.0),
                    "lam8": ("sens_lam8.csv", 8.0), "mesh61": ("sens_mesh61.csv", 5.0)}


def mode_check(workers=4):
    """Recheck near-threshold designs with CONVERGED_BUCKLING_MODES; write buckling_modes_check.csv.

    A design is rechecked when its recorded buckling factor is below its
    file's threshold x (1 + MODES_MARGIN). Only these can change: asking for
    more factors can only lower the lowest one, so a thinner step that failed
    still fails.

    Returns:
        The rows written (one per rechecked design, with an "input" label).
    """
    from concurrent.futures import ProcessPoolExecutor

    jobs, labels = [], []
    for label, (name, lam) in MODE_CHECK_FILES.items():
        path = ROOT / "results" / name
        if not path.exists():
            continue
        with open(path, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r["feasible"] == "True" and float(r["buckling_factor"]) < lam * (1.0 + MODES_MARGIN):
                    jobs.append((r, CONVERGED_BUCKLING_MODES, lam))
                    labels.append(label)
    with ProcessPoolExecutor(workers) as ex:
        rows = [dict(input=lab, **r) for lab, r in zip(labels, ex.map(_recheck, jobs))]
    out = ROOT / "results" / "buckling_modes_check.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    return rows


def main(argv=None):
    """Write results/fe_crosscheck.csv and its meta file; return 1 if any row is off by more than 2 %.

    With --modes, also run mode_check and write results/buckling_modes_check.csv.
    """
    ap = argparse.ArgumentParser(prog="python -m shellform.crosscheck",
                                 description="fe.py against shellbench.shellfe on four shells.")
    ap.add_argument("--modes", action="store_true",
                    help="also recheck near-threshold designs with more buckling factors")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args(argv)
    check_pin()
    rows = []
    with tempfile.TemporaryDirectory(prefix="shellform_xc_") as tmp:
        for c in cases():
            rows.append(compare_one(c, sized_thickness(c["design_id"]), Path(tmp) / c["design_id"]))
    res = ROOT / "results"
    with open(res / "fe_crosscheck.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    worst = {k: max(r[k] for r in rows) for k in ("disp_rel_diff", "buckling_rel_diff")}
    meta = {"shellbench_tag": SHELLBENCH_TAG, "tolerance": TOLERANCE,
            "rule": "pre-registration amendment of 31 Oct 2026: use ShellBench's wrapper if > 2 %",
            "load": "self-weight only, GRAV (0, 0, -1)", "max_rel_diff": worst,
            "all_within_tolerance": all(r["within_tolerance"] for r in rows),
            "command": "python -m shellform.crosscheck"}
    if a.modes:
        mrows = mode_check(workers=a.workers)
        moved = [f"{r['input']}:{r['design_id']}" for r in mrows if not r["passes_converged"]]
        meta["modes_check"] = {"file": "results/buckling_modes_check.csv",
                               "rechecked": len(mrows), "margin": MODES_MARGIN,
                               "buckling_factors_requested": CONVERGED_BUCKLING_MODES,
                               "max_rel_diff": max(r["rel_diff"] for r in mrows),
                               "would_fail_at_sized_thickness": moved}
        print(f"modes check: {len(mrows)} rechecked, {len(moved)} would fail: {moved}")
    else:
        # Keep the last --modes record; a plain run must not erase it.
        old = res / "fe_crosscheck_meta.json"
        if old.exists():
            prev = json.loads(old.read_text()).get("modes_check")
            if prev is not None:
                meta["modes_check"] = prev
    (res / "fe_crosscheck_meta.json").write_text(json.dumps(meta, indent=1) + "\n")
    for r in rows:
        print(f"{r['design_id']}: disp {r['disp_rel_diff']:.2e}, buckling {r['buckling_rel_diff']:.2e}")
    print(f"largest differences: disp {worst['disp_rel_diff']:.2e}, "
          f"buckling {worst['buckling_rel_diff']:.2e} (limit {TOLERANCE:.0%})")
    return 0 if meta["all_within_tolerance"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
