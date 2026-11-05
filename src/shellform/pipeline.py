"""The per-design steps that every run of ShellForm shares.

Moved here on 5 Nov 2026 (Day 8) from scripts/day04_size_10m.py and
scripts/day05_steel_carbon_10m.py, without changing a line of the
calculation, so that those two scripts and the batch runner
(shellform.batch) run exactly the same code. The scripts now import these
functions.

- size_one: form-find one design, size its thickness (pre-registration
  section 5) and run the modal analysis for S5 (Day 4).
- takeoff_one: rerun the ULS cases at the sized thickness, take off steel
  and support-zone concrete, and compute carbon with the +/-25 % band
  (Day 5, decisions D5-1 to D5-5 and P3).
- comparison: the two decision rules of pre-registration section 7.
"""

import csv
from pathlib import Path

import numpy as np

from shellform.carbon import band_corners, carbon_kgco2e, load_factors
from shellform.design_space import RESULT_COLUMNS
from shellform.designs import N_GRID, form
from shellform.fe import plan_area, run_case, surface_area
from shellform.inputs import load_inputs, shellbench_root
from shellform.pin import SHELLBENCH_TAG
from shellform.sizing import ZONE_RADIUS_SPAN_RATIO, check_as_dict, load_cases, size_design
from shellform.steel import rho_min, take_off
from shellform.strategies import envelope_thickness

ROOT = Path(__file__).resolve().parents[2]
#: Pre-registration section 7: a difference below this is "no meaningful difference".
MEANINGFUL_DIFFERENCE = 0.05
#: Extra columns of the sizing table, after RESULT_COLUMNS.
SIZING_COLUMNS = tuple(RESULT_COLUMNS) + ("surface_area_m2", "compression_zone_mpa")


def size_one(case):
    """Size one design and return (results row, list of tried checks).

    Args:
        case: One dict of shellform.design_space.design_space().

    Returns:
        (row with the SIZING_COLUMNS keys, list of dicts, one per thickness tried).
    """
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


def sized_thickness(tag="10m"):
    """Return {design_id: sized thickness [m]} from the Day 4 results of one span (tag "10m" or "20m")."""
    with open(ROOT / "results" / f"day04_sizing_{tag}.csv", newline="") as f:
        return {r["design_id"]: float(r["thickness_m"]) for r in csv.DictReader(f)
                if r["feasible"] == "True"}


def takeoff_one(args):
    """Take off steel and carbon of one sized design; return its results row.

    Args:
        args: (case dict, sized thickness [m]).
    """
    case, t = args
    inp = load_inputs()
    rho = rho_min(inp, (shellbench_root() / "docs" / "floor_concept.md").read_text(encoding="utf-8"))
    fac = load_factors()
    net, _, mid = form(case)
    span = case["span_m"]
    zone = ZONE_RADIUS_SPAN_RATIO * span
    cases, _ = load_cases(inp, case["sa_g"])
    res = {name: run_case(mid, N_GRID, net.fixed, t, inp.e_pa, inp.nu, inp.density_kg_m3, acc, w,
                          zone_radius_m=zone) for name, acc, w in cases}
    s = take_off(mid, N_GRID, t, res, inp, rho, fac.steel_density_kg_m3, zone)
    area = surface_area(mid, N_GRID)
    # Per m2 of plan area (pre-registration section 6): the plan area the shell
    # covers, which is less than span ** 2 for inset corner shells (amendment of 3 Nov 2026).
    plan = plan_area(mid, N_GRID)
    shell_m3 = t * area
    concrete = shell_m3 + s.zone_concrete_m3
    row = dict(case)
    row.update(shellbench_tag=SHELLBENCH_TAG, thickness_m=t, surface_area_m2=area, plan_area_m2=plan,
               shell_concrete_m3=shell_m3,
               zone_concrete_m3=s.zone_concrete_m3, zone_elements=s.zone_elements, zone_t_max_m=s.zone_t_max_m,
               concrete_m3=concrete, steel_kg=s.steel_kg, steel_min_kg=s.steel_min_kg,
               steel_above_min_kg=s.steel_above_min_kg, steel_from_seismic_kg=s.steel_from_seismic_kg,
               steel_demand_kg=s.demand_kg, steel_demand_from_seismic_kg=s.demand_from_seismic_kg,
               steel_kg_m2=s.steel_kg / plan, max_as_mm2_m=s.max_as_mm2_m, rho_min=s.rho_min,
               steel_governing_case=s.governing_case)
    c = carbon_kgco2e(concrete, s.steel_kg, fac)
    row.update(carbon_gbt51366_kgco2e=c, carbon_gbt51366_kgco2e_m2=c / plan,
               carbon_concrete_share=concrete * fac.concrete_kgco2e_m3 / c)
    for label, (cs, ss) in band_corners().items():
        row[f"carbon_kgco2e_m2_{label}"] = carbon_kgco2e(concrete, s.steel_kg, fac, cs, ss) / plan
    return row


def comparison(rows):
    """Apply the two decision rules of pre-registration section 7.

    Args:
        rows: Results rows of takeoff_one.

    Returns:
        One row per (supports, rise, Sa) with both strategies' carbon per m2,
        each strategy's cost of resilience (carbon at Sa / carbon at Sa = 0),
        the relative difference and the verdict, at the central factors and
        at each band corner.
    """
    labels = ["central"] + list(band_corners())

    def col(label):
        return "carbon_gbt51366_kgco2e_m2" if label == "central" else f"carbon_kgco2e_m2_{label}"

    by = {(r["supports"], r["rise_ratio"], r["strategy"], r["sa_g"]): r for r in rows}
    out = []
    for sup, rise, sa in sorted({(r["supports"], r["rise_ratio"], r["sa_g"]) for r in rows}):
        g, s = by[(sup, rise, "gravity", sa)], by[(sup, rise, "seismic", sa)]
        g0, s0 = by[(sup, rise, "gravity", 0.0)], by[(sup, rise, "seismic", 0.0)]
        o = {"span_m": g["span_m"], "supports": sup, "rise_ratio": rise, "sa_g": sa,
             "shellbench_tag": SHELLBENCH_TAG}
        verdicts = set()
        for label in labels:
            cg, cs = g[col(label)], s[col(label)]
            diff = (cs - cg) / cg
            verdict = ("no meaningful difference" if abs(diff) < MEANINGFUL_DIFFERENCE
                       else "seismic cheaper" if diff < 0 else "gravity cheaper")
            verdicts.add(verdict)
            o.update({f"gravity_kgco2e_m2_{label}": cg, f"seismic_kgco2e_m2_{label}": cs,
                      f"seismic_minus_gravity_rel_{label}": diff, f"verdict_{label}": verdict})
        o["cost_of_resilience_gravity"] = g["carbon_gbt51366_kgco2e_m2"] / g0["carbon_gbt51366_kgco2e_m2"]
        o["cost_of_resilience_seismic"] = s["carbon_gbt51366_kgco2e_m2"] / s0["carbon_gbt51366_kgco2e_m2"]
        o["verdict_same_at_all_corners"] = len(verdicts) == 1
        out.append(o)
    return out


def write_csv(rows, path):
    """Write rows (dicts with the same keys) to a CSV file."""
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
