"""tests/test_figures.py — Day 11: paper figures read only the record."""

import pytest

from shellform import figures
from shellform.sizing import LAMBDA_MIN, THICKNESS_MIN_M


def test_ratios_are_one_at_each_limit():
    f_c = 14.3e6
    row = {"span_m": "10.0", "thickness_m": str(THICKNESS_MIN_M), "buckling_factor": str(LAMBDA_MIN),
           "max_compression_mpa": "14.3", "max_deflection_m": str(10.0 / 300)}
    r = figures.ratios(row, f_c)
    assert all(v == pytest.approx(1.0) for v in r.values())


def test_record_tag_rejects_mixed_tags():
    assert figures.record_tag([{"shellbench_tag": "v1"}] * 2, "x") == "v1"
    with pytest.raises(ValueError):
        figures.record_tag([{"shellbench_tag": "v1"}, {"shellbench_tag": "v2"}], "x")


def test_governing_check_sits_at_ratio_one_in_the_record():
    """The check the sizing names as governing is the one closest to its limit."""
    from shellform.inputs import load_inputs

    f_c = load_inputs().f_c_pa
    rows = figures.read_csv(figures.BASELINE_FILE)
    assert len(rows) == 168
    for r in rows:
        rat = figures.ratios(r, f_c)
        assert max(rat.values()) <= 1.0 + 1e-9
        assert max(rat, key=rat.get) == r["governing_check"]


def test_driver_ranges_cover_every_group():
    tag, ranges = figures.driver_ranges()
    assert tag.startswith("v")
    for rng in ranges.values():
        assert len(rng) == 4
        assert all(lo <= hi for lo, hi in rng.values())
    sa = ranges[r"$S_a$ 0 to 0.6 g, gravity form"]
    assert all(abs(v - 1) < 0.05 for rng in sa.values() for v in rng)


def test_factor_status_reads_the_source_notes(tmp_path, monkeypatch):
    """Day 11: the status comes from ShellBench's file, not from typed text."""
    from shellform import carbon

    path = carbon.factors_path()
    assert carbon.factor_status().startswith("confirmed")  # pinned v0.3.0: check closed 6 Nov
    text = path.read_text(encoding="utf-8").replace("check closed", "check open")
    alt = tmp_path / "carbon_factors.csv"
    alt.write_text(text, encoding="utf-8")
    monkeypatch.setattr(carbon, "factors_path", lambda: alt)
    assert carbon.factor_status().startswith("provisional")
