"""Size one design, take off its steel and carbon, and compare the strategies.

File: src/shellform/pipeline.py

Written on Day 6 (3 Nov) so that one command runs a whole span: the Day 4
sizing (``size_one``), the Day 5 steel, support-zone and carbon take-off
(``take_off_one``) and the decision rules of pre-registration section 7
(``comparison``). The logic is that of ``scripts/day04_size_10m.py`` and
``scripts/day05_steel_carbon_10m.py``, with two changes (pre-registration
amendment of 3 Nov):

- D6-1: carbon and steel per m2 are divided by the plan area the shell
  covers (``fe.plan_area``), not by span squared. For edge-supported shells
  the two are equal; corner-supported shells cover less (D3-1).
- D6-2: the SDL and live mass added to the first-mode period uses the same
  covered plan area, because the loads are applied per plan area on the
  nodes (D4-5). Day 4 used span squared, which overstated T1 of corner
  shells (safe side for S5).

Every value comes from ShellBench through ``shellform.inputs`` and
``shellform.carbon``; the thresholds are the pre-registered ones in
``shellform.sizing``.
"""

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

#: Pre-registration section 7: a relative difference below this is "no meaningful difference".
MEANINGFUL_DIFFERENCE = 0.05


def period_with_sdl(period_concrete_s, density_kg_m3, thickness_m, area_m2, plan_m2, ge_pa, g_m_s2):
    """Return T1 with the SDL and live mass of G_E added (decision D6-2).

    CalculiX's frequency step carries the concrete mass only, so T1 is
    scaled by sqrt((m_concrete + m_GE) / m_concrete).

    Args:
        period_concrete_s: First period from CalculiX, concrete mass only [s].
        density_kg_m3: Concrete density [kg/m3].
        thickness_m: Shell thickness [m].
        area_m2: Shell surface area [m2].
        plan_m2: Plan area the shell covers [m2] (the loads act on it, D4-5).
        ge_pa: SDL + psi_E x live, per plan area [Pa].
        g_m_s2: Gravitational acceleration [m/s2].
    """
    m_self = density_kg_m3 * thickness_m * area_m2
    m_ge = ge_pa / g_m_s2 * plan_m2
    return float(period_concrete_s * np.sqrt((m_self + m_ge) / m_self))


def size_one(case):
    """Size one design (pre-registration section 5).

    Args:
        case: One design case (shellform.design_space).

    Returns:
        (row, tried): row is a dict with RESULT_COLUMNS and extra columns;
        tried is a list of the checks run at every thickness tried.
    """
    inp = load_inputs()
    net, grav, mid = form(case)
    span, sa = case["span_m"], case["sa_g"]
    best, tried = size_design(mid, N_GRID, net.fixed, span, inp, sa)
    area = surface_area(mid, N_GRID)
    plan = plan_area(mid, N_GRID)
    row = {k: "" for k in RESULT_COLUMNS}
    row.update(case)
    row.update(shellbench_tag=SHELLBENCH_TAG, feasible=best is not None,
               t_env_m=envelope_thickness(mid, grav, sa), surface_area_m2=area, plan_area_m2=plan)
    if best is not None:
        _, sls = load_cases(inp, sa)
        modal = run_case(mid, N_GRID, net.fixed, best.thickness_m, inp.e_pa, inp.nu,
                         inp.density_kg_m3, sls[0], sls[1], n_modes=1)
        row.update(thickness_m=best.thickness_m, buckling_factor=best.buckling_factor,
                   period_1_s=period_with_sdl(modal.periods_s[0], inp.density_kg_m3, best.thickness_m,
                                              area, plan, inp.sdl_pa + inp.psi_e_roof * inp.live_pa,
                                              inp.g_m_s2),
                   max_compression_mpa=best.compression_pa / 1e6,
                   compression_zone_mpa=best.compression_zone_pa / 1e6,
                   max_deflection_m=best.deflection_m)
    governing = ""
    if tried:
        below = [c for t, c in tried.items() if best is None or t < best.thickness_m]
        governing = max(below, key=lambda c: c.thickness_m).governing if below else "t_min"
    row["governing_check"] = governing
    return row, [dict(design_id=case["design_id"], **check_as_dict(c)) for c in tried.values()]


def take_off_one(case, thickness_m):
    """Take off steel, support-zone concrete and carbon of one sized design (D5-1 to D5-5).

    Args:
        case: One design case.
        thickness_m: Its sized thickness [m].

    Returns:
        Dict of take-off and carbon columns, per covered plan area (D6-1).
    """
    inp = load_inputs()
    rho = rho_min(inp, (shellbench_root() / "docs" / "floor_concept.md").read_text(encoding="utf-8"))
    fac = load_factors()
    net, _, mid = form(case)
    span = case["span_m"]
    zone = ZONE_RADIUS_SPAN_RATIO * span
    cases, _ = load_cases(inp, case["sa_g"])
    res = {name: run_case(mid, N_GRID, net.fixed, thickness_m, inp.e_pa, inp.nu, inp.density_kg_m3, acc, w,
                          zone_radius_m=zone) for name, acc, w in cases}
    s = take_off(mid, N_GRID, thickness_m, res, inp, rho, fac.steel_density_kg_m3, zone)
    area = surface_area(mid, N_GRID)
    plan = plan_area(mid, N_GRID)
    shell_m3 = thickness_m * area
    concrete = shell_m3 + s.zone_concrete_m3
    c = carbon_kgco2e(concrete, s.steel_kg, fac)
    row = dict(shell_concrete_m3=shell_m3, zone_concrete_m3=s.zone_concrete_m3, zone_elements=s.zone_elements,
               zone_t_max_m=s.zone_t_max_m, concrete_m3=concrete, steel_kg=s.steel_kg,
               steel_min_kg=s.steel_min_kg, steel_above_min_kg=s.steel_above_min_kg,
               steel_from_seismic_kg=s.steel_from_seismic_kg, steel_demand_kg=s.demand_kg,
               steel_demand_from_seismic_kg=s.demand_from_seismic_kg, steel_kg_m2=s.steel_kg / plan,
               max_as_mm2_m=s.max_as_mm2_m, rho_min=s.rho_min, steel_governing_case=s.governing_case,
               carbon_gbt51366_kgco2e=c, carbon_gbt51366_kgco2e_m2=c / plan,
               carbon_kgco2e_per_span2=c / span ** 2,
               carbon_concrete_share=concrete * fac.concrete_kgco2e_m3 / c)
    for label, (cs, ss) in band_corners().items():
        row[f"carbon_kgco2e_m2_{label}"] = carbon_kgco2e(concrete, s.steel_kg, fac, cs, ss) / plan
    return row


def comparison(rows):
    """Apply the two decision rules of pre-registration section 7, per span.

    Args:
        rows: Design rows with take-off columns (one per sized design).

    Returns:
        One row per (span, supports, rise, Sa) with both strategies' carbon
        per m2, each strategy's cost of resilience (carbon at Sa / carbon at
        Sa = 0), the relative difference and the verdict, at the central
        factors and at each band corner.
    """
    labels = ["central"] + list(band_corners())

    def col(label):
        return "carbon_gbt51366_kgco2e_m2" if label == "central" else f"carbon_kgco2e_m2_{label}"

    by = {(r["span_m"], r["supports"], r["rise_ratio"], r["strategy"], r["sa_g"]): r for r in rows}
    keys = sorted({(r["span_m"], r["supports"], r["rise_ratio"], r["sa_g"]) for r in rows})
    out = []
    for span, sup, rise, sa in keys:
        g, s = by.get((span, sup, rise, "gravity", sa)), by.get((span, sup, rise, "seismic", sa))
        g0, s0 = by.get((span, sup, rise, "gravity", 0.0)), by.get((span, sup, rise, "seismic", 0.0))
        o = {"span_m": span, "supports": sup, "rise_ratio": rise, "sa_g": sa, "shellbench_tag": SHELLBENCH_TAG}
        if None in (g, s, g0, s0):
            o["verdict_central"] = "infeasible design in this cell"
            out.append(o)
            continue
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


def headline(comp_rows, sa_min=0.2, rise=0.15):
    """Return whether the pre-registered headline claim holds (section 7).

    "Seismic-aware form-finding is cheaper" holds only if the verdict is
    "seismic cheaper" at all four band corners and the central factors, at
    rise-to-span 0.15, for both supports, at every Sa >= 0.2 g, in every span.

    Args:
        comp_rows: Rows of ``comparison``.
        sa_min: Lowest Sa of the claim [g] (section 7).
        rise: Rise-to-span ratio of the claim (section 7).

    Returns:
        (holds, cells): holds is a bool; cells lists the (span, supports, Sa)
        cells where every verdict is "seismic cheaper".
    """
    sel = [r for r in comp_rows if r["rise_ratio"] == rise and r["sa_g"] >= sa_min - 1e-9]
    cells = []
    ok = bool(sel)
    for r in sel:
        vs = [v for k, v in r.items() if k.startswith("verdict_") and k != "verdict_same_at_all_corners"]
        if vs and all(v == "seismic cheaper" for v in vs):
            cells.append((r["span_m"], r["supports"], r["sa_g"]))
        else:
            ok = False
    return ok, cells
