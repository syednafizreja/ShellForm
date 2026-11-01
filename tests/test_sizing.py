"""Tests for the ShellBench inputs and the thickness sizing."""

import numpy as np
import pytest

from shellform.fe import find_ccx, write_deck
from shellform.formfind import corner_network_for_inset, form_to_rise, square_network
from shellform.sb_inputs import DesignInputs, load_inputs, spec_value
from shellform.sizing import (ThicknessCheck, check_thickness, combination_accels, dead_load_pa,
                              effective_density, governing_check, size_shell, smallest_positive)
from shellform.strategies import seismic_mid_surface

needs_ccx = pytest.mark.skipif(find_ccx() is None, reason="CalculiX not on PATH")
# Test inputs for the arithmetic, not ShellBench values.
FAKE = DesignInputs(e_pa=3.0e10, nu=0.2, unit_weight_n_m3=2.0e4, superimposed_dead_pa=1000.0,
                    roof_live_pa=500.0, g_m_s2=10.0, gamma_g=1.3, gamma_q=1.5,
                    gamma_eg=1.3, gamma_eh=1.4)


def test_inputs_are_read_from_the_clone():
    inp = load_inputs()
    assert inp.e_pa > 0 and 0 < inp.nu < 0.5 and inp.g_m_s2 > 9
    assert inp.unit_weight_n_m3 == spec_value("X7") * 1.0e3
    assert 0 < inp.superimposed_dead_pa < spec_value("L2") * 1.0e3


def test_missing_spec_row_stops_the_run():
    with pytest.raises(ValueError):
        spec_value("ZZ99")


def test_density_carries_the_dead_load():
    t = 0.1  # dead load 2000 + 1000 = 3000 Pa
    assert dead_load_pa(t, FAKE) == pytest.approx(3000.0)
    assert effective_density(t, FAKE) * FAKE.g_m_s2 * t == pytest.approx(3000.0)


def test_combination_accelerations_reproduce_the_factored_loads():
    t = 0.1
    mass_per_area = effective_density(t, FAKE) * t
    service, gravity, seismic = combination_accels(t, 0.5, FAKE)
    assert -service[2] * mass_per_area == pytest.approx(3500.0)
    assert -gravity[2] * mass_per_area == pytest.approx(1.3 * 3000.0 + 1.5 * 500.0)
    assert -seismic[2] * mass_per_area == pytest.approx(1.3 * 3000.0)
    assert seismic[0] * mass_per_area == pytest.approx(1.4 * 0.5 * 3000.0)


def test_smallest_positive_ignores_reversed_load_modes():
    assert smallest_positive([-3.0, 7.0, 5.0]) == 5.0
    assert np.isnan(smallest_positive([-3.0]))


def test_passes_and_governing_check():
    span = 10.0
    good = ThicknessCheck(0.1, 6.0, 5.5, 0.01, 0.1)
    bad = ThicknessCheck(0.1, 6.0, 4.9, 0.01, 0.1)
    assert good.lambda_governing == 5.5 and good.passes(span) and not bad.passes(span)
    assert governing_check(bad, span) == "buckling"
    assert not ThicknessCheck(0.1, 9.0, float("nan"), 0.04, 0.1).passes(span)
    assert governing_check(ThicknessCheck(0.1, 9.0, float("nan"), 0.04, 0.1), span) == "deflection"
    assert governing_check(ThicknessCheck(0.05, 90.0, float("nan"), 0.001, 0.1), span) == "minimum_thickness"


def test_deck_leaves_out_steps_on_request():
    net = square_network(10.0, 5, "corners")
    deck = write_deck(net.xyz, 5, net.fixed, 0.1, 3e10, 0.2, 2500.0, n_modes=0,
                      static_accel=False, buckle_accel=(1.0, 0.0, -10.0))
    assert "*STATIC" not in deck and "*FREQUENCY" not in deck and "*BUCKLE" in deck


@needs_ccx
def test_four_shaking_directions_agree(tmp_path):
    """Decision D4-6: the form and the mesh make ±x and ±y equivalent."""
    inp = load_inputs()
    net, grav, _ = corner_network_for_inset(10.0, 21, 1.5, 0.10)
    mid = seismic_mid_surface(grav, 0.3, 1.5)
    lams = [check_thickness(mid, 21, net.fixed, 0.1, 0.3, inp, d, tmp_path / str(k)).lambda_seismic
            for k, d in enumerate(((1.0, 0.0), (-1.0, 0.0), (0.0, 1.0), (0.0, -1.0)))]
    assert np.ptp(lams) < 1e-3 * lams[0]


@needs_ccx
def test_body_load_scaling_is_linear(tmp_path):
    """Doubling the live load adds the expected share to the deflection."""
    net, grav, _ = corner_network_for_inset(10.0, 21, 1.5, 0.10)
    a = check_thickness(grav, 21, net.fixed, 0.1, 0.0, FAKE, workdir=tmp_path / "a")
    dbl = DesignInputs(**{**FAKE.__dict__, "roof_live_pa": 1000.0})
    b = check_thickness(grav, 21, net.fixed, 0.1, 0.0, dbl, workdir=tmp_path / "b")
    assert b.max_deflection_m / a.max_deflection_m == pytest.approx(4000.0 / 3500.0, rel=1e-3)


@needs_ccx
def test_sizing_returns_the_first_passing_step():
    inp = load_inputs()
    net = square_network(10.0, 21, "edges")
    xyz = form_to_rise(net, 1.5)
    feasible, result = size_shell(xyz, 21, net.fixed, 10.0, 0.0, inp)
    assert feasible and result.thickness_m >= 0.05
    assert result.passes(10.0)
    if result.thickness_m > 0.05:
        below = check_thickness(xyz, 21, net.fixed, result.thickness_m - 0.005, 0.0, inp)
        assert not below.passes(10.0)
