"""scripts/day05_steel_carbon_10m.py — Day 5: steel, support zones and carbon of the 84 10 m designs.

For each design in results/day04_sizing_10m.csv: rebuild the form, rerun
every ULS load case at the sized thickness, take off the reinforcement and
the thickened support-zone concrete (shellform.steel, decisions D5-1 to
D5-5), and compute A1-A3 carbon with ShellBench's factors and the +/-25 %
band (shellform.carbon, decision P3).

Writes:
- results/day05_steel_carbon_10m.csv: one row per design.
- results/day05_comparison_10m.csv: the two decision rules of
  pre-registration section 7 (cost of resilience; which strategy is cheaper,
  with the 5 % rule), at the central factors and at the four band corners.
- results/day05_meta.json: ShellBench tag, inputs, factors and their status.

These results are provisional: the carbon factors in ShellBench's file are
still marked "author to confirm", and the paper's results come from one run
after the 10 Nov freeze (pre-registration section 9).

Usage: python scripts/day05_steel_carbon_10m.py [--workers 4] [--span 20]

With --span 20 it reads results/day04_sizing_20m.csv and writes the same
files with "20m" in place of "10m" (and results/day05_meta_20m.json). The
file keeps its Day 5 name; Day 6 runs it with --span 20.
"""

import argparse
import csv
import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from shellform.carbon import FACTOR_BAND, band_corners, carbon_kgco2e, load_factors
from shellform.design_space import design_space
from shellform.designs import N_GRID, form
from shellform.fe import plan_area, run_case, surface_area
from shellform.inputs import load_inputs, shellbench_root
from shellform.pin import SHELLBENCH_TAG, check_pin
from shellform.sizing import ZONE_RADIUS_SPAN_RATIO, load_cases
from shellform.steel import rho_min, take_off

ROOT = Path(__file__).resolve().parents[1]
#: Pre-registration section 7: a difference below this is "no meaningful difference".
MEANINGFUL_DIFFERENCE = 0.05


def sized_thickness(tag="10m"):
    """Return {design_id: sized thickness [m]} from the Day 4 results of one span (tag "10m" or "20m")."""
    with open(ROOT / "results" / f"day04_sizing_{tag}.csv", newline="") as f:
        return {r["design_id"]: float(r["thickness_m"]) for r in csv.DictReader(f)
                if r["feasible"] == "True"}


def run_one(args):
    """Take off steel and carbon of one sized design; return its results row."""
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
        rows: Results rows of run_one.

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


def main():
    """Take off steel and carbon of the sized designs of one span and write the results files."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--span", type=float, default=10.0, help="span [m], one of design_space.SPANS_M")
    args = ap.parse_args()
    check_pin()
    tag = f"{args.span:g}m"
    t = sized_thickness(tag)
    cases = [(c, t[c["design_id"]]) for c in design_space(spans=(args.span,)) if c["design_id"] in t]
    with ProcessPoolExecutor(args.workers) as ex:
        rows = list(ex.map(run_one, cases))
    res = ROOT / "results"
    write_csv(rows, res / f"day05_steel_carbon_{tag}.csv")
    write_csv(comparison(rows), res / f"day05_comparison_{tag}.csv")
    fac = load_factors()
    inp = load_inputs()
    meta = {"shellbench_tag": SHELLBENCH_TAG, "grid_n": N_GRID, "inputs": inp.as_dict(),
            "rho_min": rho_min(inp, (shellbench_root() / "docs" / "floor_concept.md").read_text(encoding="utf-8")),
            "rho_min_source": "ShellBench docs/floor_concept.md, GB 50010 Table 8.5.1 note 2 (slab rule applied to the shell [J])",
            "factors": fac.__dict__, "factor_file": "ShellBench data/carbon_factors.csv at " + SHELLBENCH_TAG,
            "factor_band": FACTOR_BAND,
            "status": "provisional: every factor row in ShellBench's file is marked 'author to confirm'"}
    meta_name = "day05_meta.json" if tag == "10m" else f"day05_meta_{tag}.json"
    (res / meta_name).write_text(json.dumps(meta, indent=1) + "\n")
    print(f"wrote {len(rows)} designs")


if __name__ == "__main__":
    main()
