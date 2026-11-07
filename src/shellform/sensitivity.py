"""Sensitivity runs of pre-registration section 7 (Day 9, 6 Nov 2026).

Section 7 says: "the headline is re-checked at lambda_LBA = 3 and 8, and with
a 61 x 61 network. A conclusion that flips is reported as sensitive." The
factor band (+/-25 %, four corners, decision P3) is already part of every
baseline row, so it is summarised here from the baseline, not rerun.

Variants (each runs all 168 designs with one setting changed, nothing else):

- ``lam3``: buckling threshold lambda_LBA >= 3 instead of 5.
- ``lam8``: buckling threshold lambda_LBA >= 8 instead of 5.
- ``mesh61``: 61 x 61 form-finding and analysis network instead of 41 x 41.

The baseline is ``results/batch_all.csv`` (Day 8: all 168 through the batch
runner, 0 mismatches against the Day 4-6 record).

Usage (from the repo root, env ``shellform``):

    python -m shellform.sensitivity --run lam3 lam8 mesh61   # about 1.5 h on 4 workers
    python -m shellform.sensitivity --summarise              # tables only, seconds

Writes results/sens_<variant>.csv and _meta.json (one row per design, every
row names the ShellBench tag), results/sensitivity_cells.csv (one row per
variant and comparison cell), results/sensitivity_summary.csv (one row per
variant and span), results/sensitivity_reference.csv (the gravity form at
Sa = 0 under each setting: thickness, buckling factor, carbon and its ratio
to the baseline) and results/sensitivity_meta.json.

Like the baseline, these results are provisional until the 10 Nov freeze run
(pre-registration section 9), and the carbon factors are still "author to
confirm" in ShellBench.
"""

import argparse
import csv
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor

from shellform.batch import ccx_version, run_design, select
from shellform.carbon import band_corners
from shellform.designs import N_GRID
from shellform.pin import SHELLBENCH_TAG, check_pin
from shellform.pipeline import MEANINGFUL_DIFFERENCE, ROOT, SIZING_COLUMNS, write_csv
from shellform.sizing import LAMBDA_MIN

#: The pre-registered settings (sections 3 and 5), for the baseline row.
BASELINE = {"lambda_min": LAMBDA_MIN, "grid_n": N_GRID}
#: The section 7 variants: each changes one setting of BASELINE.
VARIANTS = {
    "lam3": {"lambda_min": 3.0},
    "lam8": {"lambda_min": 8.0},
    "mesh61": {"grid_n": 61},
}
#: Headline scope of section 7: rise-to-span and the lowest Sa of the claim.
HEADLINE_RISE = 0.15
HEADLINE_SA_MIN = 0.2
BASELINE_FILE = ROOT / "results" / "batch_all.csv"
LABELS = ("central",) + tuple(band_corners())


def carbon_column(label):
    """Return the results column of carbon per m2 of plan area at one band label."""
    return "carbon_gbt51366_kgco2e_m2" if label == "central" else f"carbon_kgco2e_m2_{label}"


def run_variant(name, workers=4):
    """Run all 168 designs with one variant's settings; write sens_<name>.csv and its meta file.

    Args:
        name: A key of VARIANTS.
        workers: Number of worker processes.

    Returns:
        List of result rows (dicts), in design-space order.
    """
    over = VARIANTS[name]
    cases = [dict(c, **over) for c in select("all")]
    t0 = time.perf_counter()
    with ProcessPoolExecutor(workers) as ex:
        out = list(ex.map(run_design, cases))
    rows = [r for r, _ in out]
    cols = list(SIZING_COLUMNS) + list(over)
    for r in rows:
        cols += [k for k in r if k not in cols]
    rows = [{k: r.get(k, "") for k in cols} for r in rows]
    write_csv(rows, ROOT / "results" / f"sens_{name}.csv")
    meta = {"shellbench_tag": SHELLBENCH_TAG, "calculix": ccx_version(), "variant": name,
            "settings": dict(BASELINE, **over), "designs": len(rows),
            "feasible": sum(1 for r in rows if r["feasible"]),
            "command": "python -m shellform.sensitivity --run " + name,
            "wall_time_s": time.perf_counter() - t0,
            "status": "provisional: carbon factors in ShellBench's file are marked 'author to confirm'",
            "tried": [c for _, t in out for c in t]}
    (ROOT / "results" / f"sens_{name}_meta.json").write_text(json.dumps(meta, indent=1) + "\n")
    return rows


def _num(v):
    """Convert one CSV cell to bool, float or str."""
    if v in ("True", "False"):
        return v == "True"
    try:
        return float(v)
    except ValueError:
        return v


def read_rows(path):
    """Read a results CSV into dicts with numbers and booleans converted."""
    with open(path, newline="") as fh:
        return [{k: _num(v) for k, v in r.items()} for r in csv.DictReader(fh)]


def verdict(carbon_gravity, carbon_seismic):
    """Apply the section 7 rule to one pair of carbon values.

    Returns:
        (relative difference (seismic - gravity) / gravity, verdict text).
    """
    diff = (carbon_seismic - carbon_gravity) / carbon_gravity
    if abs(diff) < MEANINGFUL_DIFFERENCE:
        return diff, "no meaningful difference"
    return diff, "seismic cheaper" if diff < 0 else "gravity cheaper"


def cells(rows):
    """Return one comparison row per (span, supports, rise, Sa).

    Like shellform.pipeline.comparison, but a cell where either strategy is
    infeasible gets the verdict "infeasible" (section 7: no result is dropped)
    and a cost of resilience only where both Sa and Sa = 0 are feasible.
    """
    by = {(r["span_m"], r["supports"], r["rise_ratio"], r["strategy"], r["sa_g"]): r for r in rows}
    out = []
    for span, sup, rise, sa in sorted({(r["span_m"], r["supports"], r["rise_ratio"], r["sa_g"])
                                       for r in rows}):
        g, s = by[(span, sup, rise, "gravity", sa)], by[(span, sup, rise, "seismic", sa)]
        o = {"span_m": span, "supports": sup, "rise_ratio": rise, "sa_g": sa,
             "thickness_gravity_m": g["thickness_m"], "thickness_seismic_m": s["thickness_m"],
             "governing_gravity": g["governing_check"], "governing_seismic": s["governing_check"]}
        found = set()
        for label in LABELS:
            if g["feasible"] and s["feasible"]:
                d, v = verdict(g[carbon_column(label)], s[carbon_column(label)])
            else:
                d, v = "", "infeasible"
            found.add(v)
            o[f"rel_{label}"], o[f"verdict_{label}"] = d, v
        o["verdict_same_at_all_corners"] = len(found) == 1
        for strat, r in (("gravity", g), ("seismic", s)):
            r0 = by[(span, sup, rise, strat, 0.0)]
            ok = r["feasible"] and r0["feasible"]
            o[f"cost_of_resilience_{strat}"] = (r["carbon_gbt51366_kgco2e_m2"]
                                                / r0["carbon_gbt51366_kgco2e_m2"] if ok else "")
        out.append(o)
    return out


def headline(cell_rows, span):
    """Test the section 7 headline claim at one span.

    The claim "seismic-aware form-finding is cheaper" holds only if the verdict
    is "seismic cheaper" at all four band corners, at rise-to-span 0.15, for
    both support cases, at every Sa >= 0.2 g.

    Returns:
        (holds: bool, number of scope cells, number of scope cells where it holds).
    """
    scope = [c for c in cell_rows if c["span_m"] == span and abs(c["rise_ratio"] - HEADLINE_RISE) < 1e-9
             and c["sa_g"] >= HEADLINE_SA_MIN - 1e-9]
    good = [c for c in scope if all(c[f"verdict_{lab}"] == "seismic cheaper" for lab in LABELS[1:])]
    return len(good) == len(scope) and bool(scope), len(scope), len(good)


def summarise_variant(name, rows, base_cells, base_rows):
    """Return (summary rows per span, cell rows) for one variant against the baseline."""
    cell_rows = cells(rows)
    base_by = {(c["span_m"], c["supports"], c["rise_ratio"], c["sa_g"]): c for c in base_cells}
    base_t = {r["design_id"]: r["thickness_m"] for r in base_rows}
    for c in cell_rows:
        b = base_by[(c["span_m"], c["supports"], c["rise_ratio"], c["sa_g"])]
        c["variant"] = name
        c["verdict_baseline_central"] = b["verdict_central"]
        c["flipped"] = any(c[f"verdict_{lab}"] != b[f"verdict_{lab}"] for lab in LABELS)
    summary = []
    for span in sorted({r["span_m"] for r in rows}):
        rs = [r for r in rows if r["span_m"] == span]
        cs = [c for c in cell_rows if c["span_m"] == span]
        feas = [r for r in rs if r["feasible"]]
        gov = {}
        for r in feas:
            gov[r["governing_check"]] = gov.get(r["governing_check"], 0) + 1
        verdicts = {}
        for c in cs:
            verdicts[c["verdict_central"]] = verdicts.get(c["verdict_central"], 0) + 1

        def rng(key, cs=cs):
            vals = [c[key] for c in cs if c[key] != ""]
            return (min(vals), max(vals)) if vals else ("", "")

        holds, n_scope, n_good = headline(cell_rows, span)
        cor_g, cor_s = rng("cost_of_resilience_gravity"), rng("cost_of_resilience_seismic")
        summary.append({
            # The tag the rows were run at, not the current pin (they can differ
            # after a pin move until the variant is rerun).
            "variant": name, "span_m": span,
            "shellbench_tag": ";".join(sorted({str(r.get("shellbench_tag", "")) for r in rs})),
            "designs": len(rs), "feasible": len(feas),
            "thickness_changed_vs_baseline": sum(
                1 for r in rs if r["thickness_m"] != base_t[r["design_id"]]),
            "governing_counts": "; ".join(f"{k or 'none'} {v}" for k, v in sorted(gov.items())),
            "cells": len(cs),
            "verdict_counts_central": "; ".join(f"{k} {v}" for k, v in sorted(verdicts.items())),
            "cells_same_verdict_all_corners": sum(1 for c in cs if c["verdict_same_at_all_corners"]),
            "cells_flipped_vs_baseline": sum(1 for c in cs if c["flipped"]),
            "max_abs_rel_diff_central": max((abs(c["rel_central"]) for c in cs if c["rel_central"] != ""),
                                            default=""),
            "cost_of_resilience_gravity_min": cor_g[0], "cost_of_resilience_gravity_max": cor_g[1],
            "cost_of_resilience_seismic_min": cor_s[0], "cost_of_resilience_seismic_max": cor_s[1],
            "headline_scope_cells": n_scope, "headline_cells_holding": n_good,
            "headline_holds": holds,
        })
    return summary, cell_rows


def reference_table(variant_rows):
    """Return one row per (variant, span, supports, rise) for the gravity form at Sa = 0.

    This isolates what each setting does to a design with no seismic load:
    thickness, buckling factor and carbon per m2 of plan area, and the carbon
    as a ratio of the baseline's. It is the scale against which the seismic
    effects (cost of resilience) are read.

    Args:
        variant_rows: {variant name: rows}, including "baseline".
    """
    key = lambda r: (r["span_m"], r["supports"], r["rise_ratio"])  # noqa: E731
    base = {key(r): r for r in variant_rows["baseline"]
            if r["strategy"] == "gravity" and r["sa_g"] == 0.0}
    out = []
    for name, rows in variant_rows.items():
        for r in rows:
            if r["strategy"] != "gravity" or r["sa_g"] != 0.0:
                continue
            b = base[key(r)]
            ok = r["feasible"] and b["feasible"]
            out.append({"variant": name, "span_m": r["span_m"], "supports": r["supports"],
                        "rise_ratio": r["rise_ratio"], "shellbench_tag": r.get("shellbench_tag", ""),
                        "feasible": r["feasible"], "thickness_m": r["thickness_m"],
                        "buckling_factor": r["buckling_factor"],
                        "governing_check": r["governing_check"],
                        "carbon_kgco2e_m2": r["carbon_gbt51366_kgco2e_m2"],
                        "carbon_ratio_to_baseline": (r["carbon_gbt51366_kgco2e_m2"]
                                                     / b["carbon_gbt51366_kgco2e_m2"] if ok else "")})
    return out


def summarise(variants=tuple(VARIANTS)):
    """Write the sensitivity tables from the baseline and every variant file present.

    Returns:
        The summary rows (also written to results/sensitivity_summary.csv).
    """
    base_rows = read_rows(BASELINE_FILE)
    base_cells = cells(base_rows)
    summary, all_cells = summarise_variant("baseline", base_rows, base_cells, base_rows)
    used = ["baseline"]
    variant_rows = {"baseline": base_rows}
    for name in variants:
        path = ROOT / "results" / f"sens_{name}.csv"
        if not path.exists():
            continue
        variant_rows[name] = read_rows(path)
        s, c = summarise_variant(name, variant_rows[name], base_cells, base_rows)
        summary += s
        all_cells += c
        used.append(name)
    res = ROOT / "results"
    write_csv(summary, res / "sensitivity_summary.csv")
    cols = ["variant"] + [k for k in all_cells[0] if k != "variant"]
    write_csv([{k: c[k] for k in cols} for c in all_cells], res / "sensitivity_cells.csv")
    write_csv(reference_table(variant_rows), res / "sensitivity_reference.csv")
    # The tag each input file was run at, read from its rows (every row names
    # its tag), so a summary across a pin move says which file came from where.
    file_tags = {v: sorted({r.get("shellbench_tag", "") for r in rows})
                 for v, rows in variant_rows.items()}
    # as_posix: the same text on Windows and Linux, so a laptop rerun is byte-identical.
    meta = {"shellbench_tag": SHELLBENCH_TAG, "baseline": BASELINE_FILE.relative_to(ROOT).as_posix(),
            "input_file_tags": file_tags,
            "baseline_settings": BASELINE, "variants": {v: VARIANTS.get(v, {}) for v in used},
            "headline_rule": {"rise_ratio": HEADLINE_RISE, "sa_min_g": HEADLINE_SA_MIN,
                              "band_corners": list(LABELS[1:]),
                              "meaningful_difference": MEANINGFUL_DIFFERENCE},
            "command": "python -m shellform.sensitivity --summarise",
            "status": "provisional: carbon factors in ShellBench's file are marked 'author to confirm'"}
    (res / "sensitivity_meta.json").write_text(json.dumps(meta, indent=1) + "\n")
    return summary


def main(argv=None):
    """Run the chosen variants and/or write the summary tables."""
    ap = argparse.ArgumentParser(prog="python -m shellform.sensitivity",
                                 description="Sensitivity runs of pre-registration section 7.")
    ap.add_argument("--run", nargs="+", choices=sorted(VARIANTS), default=[])
    ap.add_argument("--summarise", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args(argv)
    if not a.run and not a.summarise:
        ap.error("give --run and/or --summarise")
    check_pin()
    for name in a.run:
        rows = run_variant(name, a.workers)
        print(f"{name}: {sum(1 for r in rows if r['feasible'])} of {len(rows)} feasible "
              f"(ShellBench {SHELLBENCH_TAG})")
    if a.summarise or a.run:
        for s in summarise():
            print(f"{s['variant']:>8} L{s['span_m']:g}: {s['verdict_counts_central']}; flipped "
                  f"{s['cells_flipped_vs_baseline']}; headline {'holds' if s['headline_holds'] else 'not made'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
