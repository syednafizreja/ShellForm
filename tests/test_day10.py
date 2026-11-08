"""tests/test_day10.py — Day 10: pin (now v0.3.0), S5 plateau table, fe.py cross-check."""

import pytest

from shellform.crosscheck import cases, compare_one, shellbench_model
from shellform.designs import form, grid_n
from shellform.fe import find_ccx, write_case_deck
from shellform.inputs import load_inputs
from shellform.pin import SHELLBENCH_TAG, check_pin
from shellform.s5 import alpha_shape, branch, plateau_rows, spectrum_constants

needs_ccx = pytest.mark.skipif(find_ccx() is None, reason="CalculiX not on PATH")


def test_pin_matches_the_install():
    # Pin moved to v0.3.0 on 8 Nov 2026 (LOG.md Day 11); v0.3.0 still reports 0.2.0.
    assert SHELLBENCH_TAG == "v0.3.0"
    assert check_pin() == "v0.3.0"


def test_spectrum_constants_come_from_shellbench():
    tg, t0 = spectrum_constants()
    assert tg == 0.35 and t0 == 0.1


def test_alpha_shape_branches():
    tg, t0 = spectrum_constants()
    assert alpha_shape(0.0, tg) == pytest.approx(0.45)
    assert alpha_shape(0.05, tg) == pytest.approx(0.725)
    assert alpha_shape(0.2, tg) == pytest.approx(1.0)
    assert alpha_shape(0.7, tg) == pytest.approx(0.5 ** 0.9)
    assert [branch(t, tg, t0) for t in (0.05, 0.2, 0.35, 0.5)] == [
        "rising", "plateau", "plateau", "descending"]


def test_plateau_rows_pass_rule_and_skip_infeasible():
    tg, t0 = spectrum_constants()
    base = dict(design_id="d", shellbench_tag="v0.2.0", span_m="10.0", supports="corners",
                rise_ratio="0.15", strategy="gravity", sa_g="0.3", thickness_m="0.09")
    rows = [dict(base, feasible="True", period_1_s="0.18"),
            dict(base, feasible="True", period_1_s="0.36"),
            dict(base, feasible="False", period_1_s="")]
    out = plateau_rows(rows, tg, t0)
    assert len(out) == 2
    assert out[0]["s5_pass"] and not out[1]["s5_pass"]
    assert out[1]["branch"] == "descending" and out[1]["alpha_shape"] < 1.0


def test_case_deck_requests_the_given_number_of_buckling_factors():
    inp = load_inputs()
    case = dict(design_id="x", span_m=10.0, rise_ratio=0.15, supports="corners",
                strategy="gravity", sa_g=0.0, grid_n=9)
    net, _, mid = form(case)
    args = (mid, 9, net.fixed, 0.09, inp.e_pa, inp.nu, inp.density_kg_m3, (0, 0, -9.81), (0, 0, 0))
    assert "*BUCKLE\n1\n" in write_case_deck(*args)
    assert "*BUCKLE\n4\n" in write_case_deck(*args, n_buckle=4)


def test_shellbench_model_has_the_same_mesh_and_supports():
    inp = load_inputs()
    case = dict(design_id="x", span_m=10.0, rise_ratio=0.15, supports="corners",
                strategy="gravity", sa_g=0.0, grid_n=9)
    net, _, mid = form(case)
    m = shellbench_model(mid, 9, net.fixed, 0.09, inp.e_pa, inp.nu, inp.density_kg_m3, 9.81)
    assert len(m.elements) == 16
    assert all(first == 1 and last == 3 for _, first, last in m.supports)
    assert m.gravity == (9.81, 0.0, 0.0, -1.0)


def test_crosscheck_cases_are_four_gravity_forms():
    cs = cases()
    assert len(cs) == 4
    assert {(c["span_m"], c["supports"]) for c in cs} == {
        (10.0, "corners"), (10.0, "edges"), (20.0, "corners"), (20.0, "edges")}
    assert all(c["strategy"] == "gravity" and c["rise_ratio"] == 0.15 for c in cs)


@needs_ccx
def test_fe_agrees_with_shellbench_wrapper_on_a_small_shell(tmp_path):
    case = dict(design_id="small", span_m=10.0, rise_ratio=0.15, supports="corners",
                strategy="gravity", sa_g=0.0, grid_n=13)
    assert grid_n(case) == 13
    row = compare_one(case, 0.09, tmp_path)
    assert row["disp_rel_diff"] < 1e-6
    assert row["buckling_rel_diff"] < 0.02


def test_sizing_asks_for_four_buckling_factors():
    import inspect

    from shellform.sizing import N_BUCKLE_SIZING, check_thickness
    assert N_BUCKLE_SIZING == 4
    assert inspect.signature(check_thickness).parameters["n_buckle"].default == 4
