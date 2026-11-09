"""scripts/day13_explorer_data.py — Day 13: data file for the design explorer.

Writes explorer/explorer_data.js: one record per design (all 168), joining
the frozen baseline results (results/batch_all.csv, freeze run of 9 Nov 2026)
with the mid-surface of the form, rebuilt by shellform.designs.form (the same
builder the runs use). The file is a JavaScript assignment
(``window.SHELLFORM_DATA = {...}``) so explorer/index.html opens straight from
disk, with no server.

Nothing here computes a result: every number shown in the explorer is a
column of batch_all.csv, copied without change, except the unit changes
named below (m -> mm for thickness). Node coordinates are rounded to 1 mm
(EXPLORER_ROUND_M) and taken on every EXPLORER_STRIDE-th grid line, to keep
the file small; this affects only the picture.

Usage (from the repository root, in env ``shellform``):

    python scripts/day13_explorer_data.py
"""

import csv
import json
from pathlib import Path

from shellform.designs import N_GRID, form

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "results" / "batch_all.csv"
FREEZE_META = ROOT / "results" / "freeze_meta.json"
OUT = ROOT / "explorer" / "explorer_data.js"

#: Every k-th grid line of the 41 x 41 network is drawn: 41 -> 21 lines [J] (picture only).
EXPLORER_STRIDE = 2
#: Node coordinates rounded to this step [m] (picture only).
EXPLORER_ROUND_M = 0.001

#: Columns copied from batch_all.csv (name in file -> key in the explorer).
COLUMNS = {"design_id": "id", "span_m": "span_m", "supports": "supports", "rise_ratio": "rise_ratio",
           "strategy": "strategy", "sa_g": "sa_g", "thickness_m": "thickness_m",
           "governing_check": "governing", "buckling_factor": "buckling_factor",
           "period_1_s": "period_1_s", "steel_kg_m2": "steel_kg_m2",
           "carbon_gbt51366_kgco2e_m2": "carbon_kgco2e_m2",
           "carbon_kgco2e_m2_c-s-": "carbon_low", "carbon_kgco2e_m2_c+s+": "carbon_high",
           "carbon_concrete_share": "concrete_share", "plan_area_m2": "plan_area_m2"}
TEXT = {"design_id", "supports", "strategy", "governing_check"}


def nodes_of(row):
    """Return the drawn mid-surface nodes of one design as a flat list [m], and the drawn grid size."""
    case = {"span_m": float(row["span_m"]), "rise_ratio": float(row["rise_ratio"]),
            "supports": row["supports"], "strategy": row["strategy"], "sa_g": float(row["sa_g"])}
    _, _, mid = form(case)
    keep = [i * N_GRID + j for i in range(0, N_GRID, EXPLORER_STRIDE)
            for j in range(0, N_GRID, EXPLORER_STRIDE)]
    n = len(range(0, N_GRID, EXPLORER_STRIDE))
    flat = [round(float(v) / EXPLORER_ROUND_M) * EXPLORER_ROUND_M for k in keep for v in mid[k]]
    return [round(v, 3) for v in flat], n


def main():
    """Build explorer/explorer_data.js from the frozen baseline."""
    with open(SOURCE, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    tags = {r["shellbench_tag"] for r in rows}
    if len(tags) != 1:
        raise SystemExit(f"batch_all.csv names tags {sorted(tags)}; expected one")
    freeze = json.loads(FREEZE_META.read_text(encoding="utf-8"))
    designs = []
    for r in rows:
        d = {COLUMNS[k]: (r[k] if k in TEXT else float(r[k])) for k in COLUMNS}
        d["nodes"], d["n"] = nodes_of(r)
        designs.append(d)
    data = {"shellbench_tag": tags.pop(), "freeze_tag": freeze["freeze_tag"],
            "code_commit": freeze["code_commit"], "source": "results/batch_all.csv",
            "grid_n": N_GRID, "stride": EXPLORER_STRIDE, "designs": designs}
    OUT.write_text("window.SHELLFORM_DATA = " + json.dumps(data, separators=(",", ":")) + ";\n",
                   encoding="utf-8")
    print(f"wrote {len(designs)} designs to {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
