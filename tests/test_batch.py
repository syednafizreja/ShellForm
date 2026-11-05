"""tests/test_batch.py — Day 8: the batch runner selects, runs and checks designs."""

import pytest

from shellform.batch import RECORD_REL_TOL, _record_rows, compare_with_record, select
from shellform.fe import find_ccx

needs_ccx = pytest.mark.skipif(find_ccx() is None, reason="CalculiX not on PATH")


def test_smoke8_touches_every_span_support_and_strategy():
    cases = select("smoke8")
    assert len(cases) == 8
    assert {(c["span_m"], c["supports"], c["strategy"]) for c in cases} == {
        (s, p, g) for s in (10.0, 20.0) for p in ("corners", "edges") for g in ("gravity", "seismic")}
    assert {c["rise_ratio"] for c in cases} == {0.15} and {c["sa_g"] for c in cases} == {0.3}


def test_filters_narrow_and_all_is_168():
    assert len(select("all")) == 168
    assert len(select(spans=[10], supports=["corners"], sa=[0.0, 0.6])) == 12
    assert len(select("smoke8", spans=[20])) == 4
    ids = ["L10-edges-r0.10-gravity-sa0.0"]
    assert [c["design_id"] for c in select(ids=ids)] == ids
    with pytest.raises(ValueError):
        select(ids=["L10-nowhere"])


def _record_as_batch_row(design_id, span_m=10.0):
    """Build a batch-like row from the committed record."""
    rec = dict(_record_rows(f"{span_m:g}m")[design_id])
    rec.update(design_id=design_id, span_m=span_m)
    return rec


def test_record_check_passes_on_the_record_and_catches_changes():
    row = _record_as_batch_row("L10-corners-r0.15-seismic-sa0.3")
    summary, bad = compare_with_record([row])
    assert summary["rows_with_record"] == 1 and bad == []
    # a change of thickness (exact column) and of steel beyond the tolerance are caught
    changed = dict(row, thickness_m=str(float(row["thickness_m"]) + 0.005),
                   steel_kg=str(float(row["steel_kg"]) * (1 + 10 * RECORD_REL_TOL)))
    _, bad = compare_with_record([changed])
    assert {b["column"] for b in bad} == {"thickness_m", "steel_kg"}


@needs_ccx
def test_one_design_from_one_call_matches_the_record():
    from shellform.batch import run_design

    case = select(ids=["L10-edges-r0.15-gravity-sa0.3"])[0]
    row, tried = run_design(case)
    assert row["shellbench_tag"] and tried
    summary, bad = compare_with_record([row])
    assert summary["rows_with_record"] == 1 and bad == []
