"""tests/test_explorer.py — the explorer data file matches the frozen baseline (Day 13)."""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load():
    """Return the explorer data (dict) parsed from explorer/explorer_data.js."""
    text = (ROOT / "explorer" / "explorer_data.js").read_text(encoding="utf-8")
    return json.loads(text.split("=", 1)[1].strip().rstrip(";"))


def test_explorer_data_equals_batch_all():
    """Every number shown equals results/batch_all.csv, and all 168 designs are present."""
    data = load()
    with open(ROOT / "results" / "batch_all.csv", newline="", encoding="utf-8") as f:
        rows = {r["design_id"]: r for r in csv.DictReader(f)}
    assert len(data["designs"]) == len(rows) == 168
    assert data["shellbench_tag"] == {r["shellbench_tag"] for r in rows.values()}.pop()
    for d in data["designs"]:
        r = rows[d["id"]]
        assert d["thickness_m"] == float(r["thickness_m"])
        assert d["carbon_kgco2e_m2"] == float(r["carbon_gbt51366_kgco2e_m2"])
        assert d["buckling_factor"] == float(r["buckling_factor"])
        assert d["governing"] == r["governing_check"]
        assert len(d["nodes"]) == 3 * d["n"] ** 2
