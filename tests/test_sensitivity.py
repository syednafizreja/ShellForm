"""tests/test_sensitivity.py — Day 9: the section 7 sensitivity tables and settings."""

import pytest

from shellform.designs import N_GRID, form, grid_n
from shellform.sensitivity import (BASELINE_FILE, LABELS, VARIANTS, cells, headline, read_rows,
                                   summarise_variant, verdict)


def test_verdict_rule_uses_the_5_percent_band():
    assert verdict(100.0, 96.0)[1] == "no meaningful difference"
    assert verdict(100.0, 94.0)[1] == "seismic cheaper"
    assert verdict(100.0, 106.0)[1] == "gravity cheaper"
    assert verdict(100.0, 94.0)[0] == pytest.approx(-0.06)


def test_variants_change_one_setting_each():
    assert VARIANTS == {"lam3": {"lambda_min": 3.0}, "lam8": {"lambda_min": 8.0},
                        "mesh61": {"grid_n": 61}}


def test_grid_n_defaults_to_the_preregistered_network():
    case = dict(span_m=10.0, rise_ratio=0.15, supports="edges", strategy="gravity", sa_g=0.0)
    assert grid_n(case) == N_GRID == 41
    _, _, mid = form(dict(case, grid_n=21))
    assert mid.shape == (21 * 21, 3)


def _row(strategy, sa, carbon, feasible=True):
    """One synthetic design row for the cell table."""
    r = dict(span_m=10.0, supports="corners", rise_ratio=0.15, strategy=strategy, sa_g=sa,
             feasible=feasible, thickness_m=0.1 if feasible else "", governing_check="buckling",
             design_id=f"{strategy}{sa}")
    for lab in LABELS:
        col = "carbon_gbt51366_kgco2e_m2" if lab == "central" else f"carbon_kgco2e_m2_{lab}"
        r[col] = carbon if feasible else ""
    return r


def test_infeasible_cells_are_kept_and_named():
    rows = [_row("gravity", 0.0, 50.0), _row("seismic", 0.0, 50.0),
            _row("gravity", 0.2, 50.0), _row("seismic", 0.2, 40.0, feasible=False)]
    out = {c["sa_g"]: c for c in cells(rows)}
    assert out[0.0]["verdict_central"] == "no meaningful difference"
    assert out[0.2]["verdict_central"] == "infeasible"
    assert out[0.2]["cost_of_resilience_seismic"] == ""
    assert out[0.2]["cost_of_resilience_gravity"] == pytest.approx(1.0)


def test_headline_needs_every_scope_cell_at_every_corner():
    rows = []
    for sup in ("corners", "edges"):
        for sa in (0.0, 0.2, 0.3):
            for strat, c in (("gravity", 50.0), ("seismic", 40.0 if sa > 0 else 50.0)):
                rows.append(dict(_row(strat, sa, c), supports=sup))
    holds, n, good = headline(cells(rows), 10.0)
    assert (holds, n, good) == (True, 4, 4)
    rows[-1] = dict(_row("seismic", 0.3, 49.0), supports="edges")
    holds, n, good = headline(cells(rows), 10.0)
    assert (holds, n, good) == (False, 4, 3)


def test_baseline_summary_reproduces_the_record_verdicts():
    base = read_rows(BASELINE_FILE)
    base_cells = cells(base)
    summary, _ = summarise_variant("baseline", base, base_cells, base)
    by_span = {s["span_m"]: s for s in summary}
    # 7 Nov record (D10-1, 4 buckling factors): 37 + 5 cells at 10 m, 42 at 20 m;
    # headline not made. (Days 5-9, 1 factor: 36 + 6.)
    assert by_span[10.0]["verdict_counts_central"] == "no meaningful difference 37; seismic cheaper 5"
    assert by_span[20.0]["verdict_counts_central"] == "no meaningful difference 42"
    assert not by_span[10.0]["headline_holds"] and not by_span[20.0]["headline_holds"]
    assert all(s["cells_flipped_vs_baseline"] == 0 for s in summary)


def test_reference_table_is_one_against_itself():
    from shellform.sensitivity import reference_table

    base = read_rows(BASELINE_FILE)
    ref = reference_table({"baseline": base})
    assert len(ref) == 12  # 2 spans x 2 supports x 3 rises, gravity at Sa = 0
    assert all(r["carbon_ratio_to_baseline"] == pytest.approx(1.0) for r in ref)
