"""scripts/day14_paper_tables.py

Build the manuscript tables (Methods and Results) from the frozen record.

Every value in every table is read from ``results/`` (freeze run, tag
``freeze-2026-11-09``), from ShellBench at the pinned tag (through
``shellform.inputs`` and ``shellform.carbon``), or computed here by the frozen
code in ``src/shellform`` (tests S1-S3 on the 41 x 41 networks). Nothing is
typed in by hand. Each table names the ShellBench tag it used.

Run from the repository root:

    python scripts/day14_paper_tables.py            # all tables
    python scripts/day14_paper_tables.py --no-s123  # skip the S1-S3 recompute

Output: ``paper/tables/*.md`` (Markdown, for drafting) and
``paper/tables/tables.json`` (the same values, for tests and the numbers
ledger). Table S1 (all 168 designs) is also written as CSV.
"""

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUT = ROOT / "paper" / "tables"
FREEZE_TAG = "freeze-2026-11-09"


def read_csv(name):
    """Read a CSV file from results/ as a list of dicts (strings)."""
    with open(RESULTS / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_json(name):
    """Read a JSON file from results/."""
    return json.loads((RESULTS / name).read_text(encoding="utf-8"))


def one_tag(rows, name):
    """Return the single ShellBench tag named in a result file, or fail.

    Args:
        rows: Rows with a ``shellbench_tag`` column.
        name: File name, for the error message.
    """
    tags = {r["shellbench_tag"] for r in rows}
    if len(tags) != 1:
        raise ValueError(f"{name} mixes ShellBench tags: {sorted(tags)}")
    return tags.pop()


def rng(values, fmt):
    """Format a min-max range; a single value if min equals max after formatting."""
    lo, hi = fmt.format(min(values)), fmt.format(max(values))
    return lo if lo == hi else f"{lo}-{hi}"


def md_table(header, rows):
    """Return a Markdown table as text."""
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def write_md(stem, title, intro, header, rows, notes, tag):
    """Write one table file with its provenance line.

    Args:
        stem: File name without extension.
        title: Table title (draft caption; the author rewrites it).
        intro: One line saying what the table is for.
        header, rows: Table content.
        notes: Footnote lines (sources, clauses, [J] marks).
        tag: ShellBench tag of the record the table reads.
    """
    text = [f"# {title}", "", intro, "", md_table(header, rows), ""]
    text += [f"- {n}" for n in notes]
    text += ["", f"Built by `python scripts/day14_paper_tables.py` from the freeze record ({FREEZE_TAG}); "
             f"ShellBench {tag}. Do not edit by hand; rerun the script.", ""]
    (OUT / f"{stem}.md").write_text("\n".join(text), encoding="utf-8")


# ---------------------------------------------------------------- Methods


def table_design_space():
    """Table 1: the design space, from shellform.design_space."""
    from shellform import design_space as ds

    cases = ds.design_space()
    rows = [["Plan", "square"],
            ["Span L [m]", ", ".join(f"{s:g}" for s in ds.SPANS_M)],
            ["Supports", "four corners; four continuous edges"],
            ["Rise-to-span ratio [-]", ", ".join(f"{r:.2f}" for r in ds.RISE_RATIOS)],
            ["Form-finding strategy", "gravity-only; seismic-aware"],
            ["Plateau spectral acceleration Sa [g]", ", ".join(f"{a:.1f}" for a in ds.SA_LEVELS_G)],
            ["Designs", f"{len(cases)}"]]
    return {"designs": len(cases)}, rows


def table_inputs():
    """Table 2: material values, loads and factors read from ShellBench."""
    from shellform.inputs import load_inputs
    from shellform import carbon

    d = load_inputs()
    f = carbon.load_factors()
    rows = [
        ["Concrete elastic modulus E_c", f"{d.e_pa / 1e9:.1f} GPa", d.sources["e_pa"]],
        ["Poisson's ratio ν_c", f"{d.nu:.1f}", d.sources["nu"]],
        ["Reinforced concrete unit weight", f"{d.unit_weight_n_m3 / 1e3:.1f} kN/m³", d.sources["unit_weight_n_m3"]],
        ["Superimposed dead load (plan)", f"{d.sdl_pa / 1e3:.3f} kPa", d.sources["sdl_pa"]],
        ["Roof live load, non-accessible (plan)", f"{d.live_pa / 1e3:.1f} kPa", d.sources["live_pa"]],
        ["Concrete design compressive strength f_c", f"{d.f_c_pa / 1e6:.1f} MPa", d.sources["f_c_pa"]],
        ["Concrete design tensile strength f_t", f"{d.f_t_pa / 1e6:.2f} MPa", d.sources["f_t_pa"]],
        ["Steel design yield strength f_y", f"{d.f_y_pa / 1e6:.0f} MPa", d.sources["f_y_pa"]],
        ["Partial factors γ_G, γ_Q", f"{d.gamma_g:g}, {d.gamma_q:g}", "combinations.GAMMA_G, GAMMA_Q"],
        ["Seismic combination γ_EG, γ_Eh", f"{d.gamma_eg:g}, {d.gamma_eh:g}", d.sources["gamma_eg"]],
        ["Live load share in G_E (roof)", f"{d.psi_e_roof:g}", d.sources["psi_e_roof"]],
        ["Characteristic period T_g", f"{d.tg_s:.2f} s", d.sources["tg_s"]],
    ]
    band = "data/carbon_factors.csv via carbon.load_factors(), ±25 % band"
    rows.append([f"Carbon factor, {f.concrete_material} concrete", f"{f.concrete_kgco2e_m3:g} kgCO₂e/m³", f"{f.set_name}; {band}"])
    rows.append([f"Carbon factor, {f.steel_material} bar steel", f"{f.steel_kgco2e_kg:g} kgCO₂e/kg", f"{f.set_name}; {band}"])
    return {"inputs": {k: v for k, v in d.as_dict().items() if k != "sources"}, "factors": {"set": f.set_name, "concrete_kgco2e_m3": f.concrete_kgco2e_m3, "steel_kgco2e_kg": f.steel_kgco2e_kg}}, rows


def _network_cases():
    """The four baseline networks (rise 0.15) used for S1-S3."""
    return [{"span_m": s, "supports": sp, "rise_ratio": 0.15, "strategy": "seismic", "sa_g": 0.6}
            for s in (10.0, 20.0) for sp in ("corners", "edges")]


def s123_errors():
    """Recompute tests S1-S3 on the four 41 x 41 baseline networks (rise 0.15).

    S1: seismic-aware mid-surface at Sa = 0 against the gravity form (max |dx| [m]).
    S2: nodal equilibrium of the thrust surface at Sa = 0.6 g in +x, relative to the load.
    S3: rotating loads and supports by 0.4 rad and pi/2 rotates the form (relative error).

    Returns:
        Dict of worst values over the four networks.
    """
    from shellform.checks import equilibrium_error, rotation_error
    from shellform.designs import form
    from shellform.formfind import Network, plan_loads, solve
    from shellform.strategies import seismic_mid_surface

    s1 = s2 = s3 = 0.0
    for case in _network_cases():
        net, grav, _ = form(case)
        rise = case["rise_ratio"] * case["span_m"]
        s1 = max(s1, float(np.abs(seismic_mid_surface(grav, 0.0, rise) - grav).max()))
        loads = plan_loads(net, sa_x=case["sa_g"])
        thrust = solve(net, loads)
        s2 = max(s2, equilibrium_error(thrust, net.edges, net.q, loads, net.free))

        def run(sup_xyz, p, net=net):
            trial = Network(sup_xyz, net.edges, net.q, net.fixed, net.free, net.boundary_edge)
            return solve(trial, p)

        for angle in (0.4, np.pi / 2):
            s3 = max(s3, rotation_error(run, net.xyz, loads, angle))
    return {"s1_max_abs_m": s1, "s2_rel": s2, "s3_rel": s3}


def table_validation(s123):
    """Table 3: tests S1-S5 and the solver cross-check, with the tolerances set in advance."""
    s4 = read_json("day07_s4_meta.json")
    s5 = read_csv("s5_summary.csv")
    base = [r for r in s5 if r["input"] == "baseline"]
    tag = one_tag(base, "s5_summary.csv")
    fails = sum(int(r["fail"]) for r in s5)
    t1 = [float(r["t1_min_s"]) for r in base] + [float(r["t1_max_s"]) for r in base]
    t1_all = max(float(r["t1_max_s"]) for r in s5)
    from shellform.crosscheck import TOLERANCE
    xc = read_csv("fe_crosscheck.csv")
    worst_b = max(abs(float(r["buckling_rel_diff"])) for r in xc)
    worst_d = max(abs(float(r["disp_rel_diff"])) for r in xc)
    rows = []
    if s123:
        rows += [
            ["S1 zero lateral load", "seismic-aware form at Sa = 0 equals the gravity form", "machine precision",
             f"largest Δx = {s123['s1_max_abs_m']:.1e} m (four 41 × 41 networks)", "pass" if s123["s1_max_abs_m"] < 1e-9 else "FAIL"],
            ["S2 nodal equilibrium", "every free node in equilibrium under gravity + 0.6 g", "< 1e-9 of the load",
             f"{s123['s2_rel']:.1e}", "pass" if s123["s2_rel"] < 1e-9 else "FAIL"],
            ["S3 rotation", "rotating loads and supports rotates the form", "< 1e-9",
             f"{s123['s3_rel']:.1e}", "pass" if s123["s3_rel"] < 1e-9 else "FAIL"]]
    worst = max(s4["worst_errors"].values())
    rows += [
        ["S4 published case (fallback)", "closed-form lean of a parabolic arch under uniform horizontal acceleration",
         f"< {s4['tolerance']:g}", f"{worst:.1e} ({s4['n_arch_cases']} arch, {s4['n_shell_cases']} shell cases)",
         "pass" if s4["passed"] else "FAIL"],
        ["S5 plateau", "first-mode period T1 of every sized design ≤ T_g", "0 failures",
         f"baseline T1 {rng(t1, '{:.3f}')} s; longest in any variant {t1_all:.3f} s; {fails} failures",
         "pass" if fails == 0 else "FAIL"],
        ["Solver cross-check", "fe.py against shellbench.shellfe, four gravity shells", f"displacement and first buckling factor within {TOLERANCE * 100:g} %",
         f"displacement {worst_d:.1e}; buckling factor within {worst_b * 100:.2f} %",
         "pass" if all(r["within_tolerance"] == "True" for r in xc) else "FAIL"]]
    data = {"s123": s123, "s4_worst": worst, "s5_failures": fails, "s5_t1_baseline": [min(t1), max(t1)],
            "s5_t1_max_any": t1_all, "crosscheck_buckling_rel": worst_b, "crosscheck_disp_rel": worst_d}
    return data, rows, tag


# ---------------------------------------------------------------- Results


def table_sized_groups():
    """Table 4: sized designs by span, supports and rise (both strategies, all Sa)."""
    rows_in = read_csv("batch_all.csv")
    tag = one_tag(rows_in, "batch_all.csv")
    groups = defaultdict(list)
    for r in rows_in:
        groups[(float(r["span_m"]), r["supports"], float(r["rise_ratio"]))].append(r)
    rows, data = [], []
    for (span, sup, rise), g in sorted(groups.items()):
        gov = sorted({r["governing_check"] for r in g})
        t = [float(r["thickness_m"]) * 1e3 for r in g]
        lam = [float(r["buckling_factor"]) for r in g]
        t1 = [float(r["period_1_s"]) for r in g]
        st = [float(r["steel_kg"]) for r in g]
        cg = [float(r["carbon_gbt51366_kgco2e_m2"]) for r in g]
        share = [float(r["carbon_concrete_share"]) * 100 for r in g]
        feas = sum(r["feasible"] == "True" for r in g)
        rows.append([f"{span:g}", sup, f"{rise:.2f}", f"{feas}/{len(g)}", ", ".join(gov), rng(t, "{:.0f}"),
                     rng(lam, "{:.2f}"), rng(t1, "{:.3f}"), rng(st, "{:.0f}"), rng(cg, "{:.1f}"), rng(share, "{:.1f}")])
        data.append({"span_m": span, "supports": sup, "rise_ratio": rise, "designs": len(g), "feasible": feas,
                     "governing": gov, "thickness_mm": [min(t), max(t)], "carbon_kgco2e_m2": [min(cg), max(cg)]})
    return data, rows, tag


def table_verdicts():
    """Table 5: verdicts of the pre-registered rule, per span and run."""
    s = read_csv("sensitivity_summary.csv")
    tag = one_tag(s, "sensitivity_summary.csv")
    names = {"baseline": "baseline (λ ≥ 5, 41 × 41)", "lam3": "λ ≥ 3", "lam8": "λ ≥ 8", "mesh61": "61 × 61 network"}
    rows, data = [], []
    for r in s:
        rows.append([names.get(r["variant"], r["variant"]), f"{float(r['span_m']):g}", f"{r['feasible']}/{r['designs']}",
                     r["thickness_changed_vs_baseline"], r["verdict_counts_central"],
                     f"{r['cells_same_verdict_all_corners']}/{r['cells']}", f"{float(r['max_abs_rel_diff_central']) * 100:.1f}",
                     f"{r['headline_cells_holding']}/{r['headline_scope_cells']}", "yes" if r["headline_holds"] == "True" else "no"])
        data.append({k: r[k] for k in ("variant", "span_m", "verdict_counts_central", "headline_cells_holding",
                                       "headline_scope_cells", "headline_holds")})
    return data, rows, tag


def table_all_designs():
    """Table S1: every sized design (supplement), as CSV and Markdown."""
    src = read_csv("batch_all.csv")
    tag = one_tag(src, "batch_all.csv")
    cols = [("design_id", "design", None), ("thickness_m", "t [mm]", lambda v: f"{float(v) * 1e3:.0f}"),
            ("governing_check", "governs", None), ("buckling_factor", "λ [-]", lambda v: f"{float(v):.2f}"),
            ("period_1_s", "T1 [s]", lambda v: f"{float(v):.3f}"), ("steel_kg", "steel [kg]", lambda v: f"{float(v):.0f}"),
            ("carbon_gbt51366_kgco2e_m2", "carbon [kgCO₂e/m²]", lambda v: f"{float(v):.1f}"),
            ("carbon_kgco2e_m2_c-s-", "band low", lambda v: f"{float(v):.1f}"),
            ("carbon_kgco2e_m2_c+s+", "band high", lambda v: f"{float(v):.1f}")]
    rows = [[(fn(r[k]) if fn else r[k]) for k, _, fn in cols] for r in src]
    with open(OUT / "tableS1_all_designs.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([h for _, h, _ in cols] + ["shellbench_tag"])
        w.writerows([row + [tag] for row in rows])
    return rows, [h for _, h, _ in cols], tag


def main(argv=None):
    """Build every table; return the summary dict written to tables.json."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--no-s123", action="store_true", help="skip the S1-S3 recompute (no form-finding)")
    args = ap.parse_args(argv)
    sys.path.insert(0, str(ROOT / "src"))
    from shellform.pin import SHELLBENCH_TAG

    OUT.mkdir(parents=True, exist_ok=True)
    summary = {"freeze_tag": FREEZE_TAG, "shellbench_tag": SHELLBENCH_TAG}

    d, rows = table_design_space()
    write_md("table1_design_space", "Table 1. Design space",
             "Methods 2.2. Pre-registration section 3; coded in `src/shellform/design_space.py`.",
             ["Variable", "Levels"], rows,
             ["Each design is sized separately; uniform thickness per shell (pre-registration section 5).",
              "Corner-supported free edges are drawn in by 0.10 × span (decision D3-1) [J]."], SHELLBENCH_TAG)
    summary["table1"] = d

    try:
        d, rows = table_inputs()
        write_md("table2_inputs", "Table 2. Material values, loads and factors",
                 "Methods 2.4 and 2.6. Every value is read from ShellBench at the pinned tag (`src/shellform/inputs.py`, "
                 "`src/shellform/carbon.py`); none is typed into ShellForm (CONTRIBUTING.md rule 2).",
                 ["Quantity", "Value", "ShellBench source"], rows,
                 ["Code clauses named in the source column are as ShellBench records them; confirm each in your copy of "
                  "the code (GB 50010-2010 (2015), GB 55002-2021, GB 50011-2010, GB/T 51366-2019).",
                  "Superimposed dead load = roof dead load less the 0.12 m slab it includes [J] (inputs.py)."],
                 SHELLBENCH_TAG)
        summary["table2"] = d
    except ImportError as exc:  # ShellBench not installed: keep the other tables
        print(f"table 2 skipped: {exc}")

    s123 = None if args.no_s123 else s123_errors()
    d, rows, tag = table_validation(s123)
    write_md("table3_validation", "Table 3. Validation tests and their results",
             "Methods 2.8. Tolerances were fixed in pre-registration section 8 before any design run.",
             ["Test", "What it shows", "Pass if", "Result", "Status"], rows,
             ["S1-S3 recomputed by this script on the 41 × 41 baseline networks (rise 0.15, both spans and supports).",
              "S4: fallback case of the 4 Nov amendment; it checks the solver against a closed form, not against "
              "Michiels & Adriaenssens' published arch (`results/day07_s4_meta.json`).",
              "S5: `results/s5_summary.csv`; baseline and the λ 3, λ 8 and 61 × 61 runs.",
              "Cross-check: `results/fe_crosscheck.csv`; tolerance `crosscheck.TOLERANCE`, the 2 % ShellBench validated its wrapper to (pre-registration section 8)."],
             tag)
    summary["table3"] = d

    d, rows, tag = table_sized_groups()
    write_md("table4_sized_designs", "Table 4. Sized designs by span, supports and rise",
             "Results 3.2. Ranges over both strategies and all seven Sa levels (14 designs per row).",
             ["L [m]", "supports", "rise/span", "feasible", "governing check", "t [mm]", "λ [-]", "T1 [s]",
              "steel [kg]", "carbon [kgCO₂e/m² plan]", "concrete share [%]"], rows,
             ["Carbon at the central factors (GB/T 51366-2019, read from ShellBench); band corners in Table S1.",
              "Source: `results/batch_all.csv`."], tag)
    summary["table4"] = d

    d, rows, tag = table_verdicts()
    write_md("table5_verdicts", "Table 5. Pre-registered comparison under the baseline and the three sensitivity runs",
             "Results 3.3 and 3.4. Rule of pre-registration section 7: a difference below 5 % is no meaningful difference.",
             ["run", "L [m]", "feasible", "thickness changed vs baseline", "verdicts (central factors)",
              "same verdict at all four band corners", "largest difference, absolute [%]", "headline scope cells holding",
              "headline made"], rows,
             ["Source: `results/sensitivity_summary.csv`. Headline scope: rise 0.15, both supports, Sa ≥ 0.2 g (10 cells per span)."],
             tag)
    summary["table5"] = d

    rows, header, tag = table_all_designs()
    write_md("tableS1_all_designs", "Table S1. All 168 sized designs (supplement)",
             "Supplement. Same values as `tableS1_all_designs.csv`.", header, rows,
             ["Carbon per m² of plan area; band low = both factors -25 %, band high = both +25 %.",
              "Source: `results/batch_all.csv`."], tag)

    (OUT / "tables.json").write_text(json.dumps(summary, indent=1, default=float), encoding="utf-8")
    print(f"tables written to {OUT.relative_to(ROOT)} (ShellBench {SHELLBENCH_TAG})")
    return summary


if __name__ == "__main__":
    main()
