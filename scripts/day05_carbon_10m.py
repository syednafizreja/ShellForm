"""scripts/day05_carbon_10m.py — Day 5: steel, support zones and carbon, 10 m designs.

Takes the Day 4 thicknesses from results/day04_sizing_10m.csv, re-runs the ULS
cases at them, and stops if any lambda or compression differs from that file.
Rules: docs/preregistration.md, amendment of 2 Nov 2026 (D5-1 to D5-6).

Writes, each naming the ShellBench tag:
- results/day05_carbon_10m.csv: one row per design.
- results/day05_strategies_10m.csv: strategy comparison at each factor-band corner.
- results/day05_mesh_check.csv: zone concrete and steel at 41 and 61 nodes per side.

Provisional: 10 m only. The headline waits for the 20 m designs.

Usage: python scripts/day05_carbon_10m.py [--workers 4]
"""

import argparse
import csv
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from shellform.design_space import design_id
from shellform.fe import corner_zone, run_case
from shellform.formfind import corner_network_for_inset, form_to_rise, square_network
from shellform.inputs import load_carbon_factors, load_inputs, rho_min_slab
from shellform.pin import SHELLBENCH_TAG, check_pin
from shellform.quantities import band_corners, carbon_kg, cheaper_strategy, shell_quantities
from shellform.sizing import ZONE_RADIUS_SPAN_RATIO, load_cases
from shellform.strategies import seismic_mid_surface

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
N_GRID = 41                     # pre-registration section 3
N_MESH_CHECK = 61               # pre-registration section 7
CORNER_EDGE_INSET_RATIO = 0.10  # decision D3-1 [J]
MATCH_TOL = 1e-4                # largest relative difference from the Day 4 file
MESH_CHECK_DESIGNS = (("corners", 0.15, "gravity", 0.3), ("corners", 0.15, "seismic", 0.1),
                      ("corners", 0.15, "seismic", 0.2), ("corners", 0.15, "seismic", 0.3),
                      ("corners", 0.15, "seismic", 0.4), ("corners", 0.15, "seismic", 0.5),
                      ("corners", 0.15, "seismic", 0.6))  # the rows where the strategies differ


def form(span, supports, rise_ratio, strategy, sa, n):
    """Return (network, mid-surface) for one design at n nodes per side."""
    rise = rise_ratio * span
    if supports == "corners":
        net, grav, _ = corner_network_for_inset(span, n, rise, CORNER_EDGE_INSET_RATIO)
    else:
        net = square_network(span, n, "edges")
        grav = form_to_rise(net, rise)
    return net, grav.copy() if strategy == "gravity" else seismic_mid_surface(grav, sa, rise)


def quantities_of(span, supports, rise_ratio, strategy, sa, t, n, inp):
    """Run the ULS cases at thickness t and return (Quantities, lambda, compression [Pa])."""
    net, mid = form(span, supports, rise_ratio, strategy, sa, n)
    zone_r = ZONE_RADIUS_SPAN_RATIO * span
    res = {}
    for name, acc, w in load_cases(inp, sa)[0]:
        res[name] = run_case(mid, n, net.fixed, t, inp.e_pa, inp.nu, inp.density_kg_m3,
                             acc, w, zone_radius_m=zone_r)
    seismic = res.get("uls_seismic_px")
    q = shell_quantities(mid, n, t, res["uls_gravity"].face_stress_pa,
                         None if seismic is None else seismic.face_stress_pa,
                         inp.f_c_pa, inp.f_y_pa, rho_min_slab(inp.f_t_pa, inp.f_y_pa),
                         load_carbon_factors()["steel_density_kg_m3"], corner_zone(mid, n, zone_r))
    return q, min(r.buckling_factor for r in res.values()), max(r.compression_pa for r in res.values())


def run_row(row):
    """Return the results row of one Day 4 design."""
    inp = load_inputs()
    factors = load_carbon_factors()
    span, sa, t = float(row["span_m"]), float(row["sa_g"]), float(row["thickness_m"])
    q, lam, comp = quantities_of(span, row["supports"], float(row["rise_ratio"]), row["strategy"], sa, t, N_GRID, inp)
    for label, new, old in (("lambda", lam, float(row["buckling_factor"])),
                            ("compression", comp / 1e6, float(row["max_compression_mpa"]))):
        if abs(new - old) > MATCH_TOL * abs(old):
            raise RuntimeError(f"{row['design_id']}: {label} {new} differs from Day 4 {old}")
    carbon = carbon_kg(q.concrete_m3, q.steel_kg, factors)
    out = {"design_id": row["design_id"], "shellbench_tag": SHELLBENCH_TAG, "span_m": span,
           "supports": row["supports"], "rise_ratio": row["rise_ratio"], "strategy": row["strategy"],
           "sa_g": sa, "thickness_m": t, "governing_check": row["governing_check"]}
    out.update(q.as_dict())
    out.update(carbon_gbt51366_kgco2e=carbon, carbon_gbt51366_kgco2e_m2=carbon / q.plan_area_m2,
               carbon_kgco2e_m2_each_face=carbon_kg(q.concrete_m3, q.steel_kg_each_face, factors) / q.plan_area_m2,
               steel_kg_m2=q.steel_kg / q.plan_area_m2)
    return out


def strategy_rows(rows, factors):
    """Return the strategy comparison at the central factors and each band corner.

    Args:
        rows: Design rows from run_row.
        factors: Output of load_carbon_factors.

    Returns:
        One row per (supports, rise, Sa), naming the verdict at each corner.
    """
    by = {(r["supports"], r["rise_ratio"], r["sa_g"], r["strategy"]): r for r in rows}
    out = []
    for (sup, rise, sa, strat), g in by.items():
        if strat != "gravity":
            continue
        s = by[(sup, rise, sa, "seismic")]

        def per_m2(r, cs, ss):
            return carbon_kg(r["concrete_m3"], r["steel_kg"], factors, cs, ss) / r["plan_area_m2"]

        c_g, c_s = per_m2(g, 1.0, 1.0), per_m2(s, 1.0, 1.0)
        row = {"shellbench_tag": SHELLBENCH_TAG, "supports": sup, "rise_ratio": rise, "sa_g": sa,
               "gravity_kgco2e_m2": c_g, "seismic_kgco2e_m2": c_s, "seismic_vs_gravity": c_s / c_g - 1.0,
               "verdict": cheaper_strategy(c_g, c_s),
               "verdict_each_face": cheaper_strategy(g["carbon_kgco2e_m2_each_face"], s["carbon_kgco2e_m2_each_face"]),
               "verdict_total_kg": cheaper_strategy(g["carbon_gbt51366_kgco2e"], s["carbon_gbt51366_kgco2e"])}
        for cs, ss in band_corners():
            row[f"verdict_c{cs}_s{ss}"] = cheaper_strategy(per_m2(g, cs, ss), per_m2(s, cs, ss))
        out.append(row)
    return out


def write_csv(path, rows):
    """Write rows of dicts to a CSV file."""
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def mesh_row(job):
    """Return the mesh-check row for (supports, rise, strategy, Sa, t, n)."""
    sup, rise, strat, sa, t, n = job
    q, lam, _ = quantities_of(10.0, sup, rise, strat, sa, t, n, load_inputs())
    return {"shellbench_tag": SHELLBENCH_TAG, "design_id": design_id(10.0, sup, rise, strat, sa), "n": n,
            "thickness_m": t, "lambda": lam, "concrete_added_m3": q.concrete_added_m3,
            "concrete_uniform_m3": q.concrete_uniform_m3, "steel_kg": q.steel_kg,
            "steel_zone_kg": q.steel_zone_kg, "steel_kg_min_only": q.steel_kg_min_only,
            "tension_ratio_max": q.tension_ratio_max}


def main():
    """Compute quantities and carbon of the 10 m designs and write the results."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    check_pin()
    with open(RESULTS / "day04_sizing_10m.csv", newline="") as f:
        day4 = list(csv.DictReader(f))
    t_of = {r["design_id"]: float(r["thickness_m"]) for r in day4}
    jobs = [(s, r, st, sa, t_of[design_id(10.0, s, r, st, sa)], n)
            for s, r, st, sa in MESH_CHECK_DESIGNS for n in (N_GRID, N_MESH_CHECK)]
    with ProcessPoolExecutor(args.workers) as ex:
        rows = list(ex.map(run_row, day4))
        mesh = list(ex.map(mesh_row, jobs))
    base = {(r["supports"], r["rise_ratio"], r["strategy"]): r["carbon_gbt51366_kgco2e_m2"]
            for r in rows if r["sa_g"] == 0.0}
    for r in rows:
        r["resilience_ratio"] = r["carbon_gbt51366_kgco2e_m2"] / base[(r["supports"], r["rise_ratio"], r["strategy"])]
    write_csv(RESULTS / "day05_carbon_10m.csv", rows)
    write_csv(RESULTS / "day05_strategies_10m.csv", strategy_rows(rows, load_carbon_factors()))
    write_csv(RESULTS / "day05_mesh_check.csv", mesh)
    print(f"wrote {len(rows)} designs")


if __name__ == "__main__":
    main()
