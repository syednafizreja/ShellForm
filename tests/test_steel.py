"""Tests for the steel and support-zone take-off (src/shellform/steel.py) and carbon (carbon.py)."""

import numpy as np
import pytest

from shellform.carbon import FACTOR_BAND, band_corners, carbon_kgco2e, factors_path, load_factors
from shellform.fe import surface_area
from shellform.formfind import form_to_rise, square_network
from shellform.inputs import load_inputs, shellbench_root
from shellform.steel import (element_areas, element_frames, rho_min, rho_min_rule, symmetric_envelope,
                             take_off, tension_per_width)

N = 9  # small grid for the unit tests: 4 x 4 elements


def flat_grid(n=N, span=4.0):
    """Return a flat n x n grid of nodes on [0, span]^2 (node k = j*n + i)."""
    x = np.linspace(0.0, span, n)
    xx, yy = np.meshgrid(x, x)  # [j, i]
    return np.stack([xx.ravel(), yy.ravel(), np.zeros(n * n)], axis=1)


def faces(n_el, comp):
    """Return a face-stress array with the same components on both faces."""
    out = np.zeros((n_el, 2, 6))
    out[:, :, :] = comp
    return out


def test_rho_min_rule_reads_the_floor_concept_wording():
    text = "- **Minimum steel.** note 2: the larger of 0.30 % and 50 f_t / f_y. For ..."  # test input
    assert rho_min_rule(text) == (pytest.approx(0.003), 50.0)
    with pytest.raises(KeyError):
        rho_min_rule("no rule here")


def test_rho_min_comes_from_shellbench_in_percent():
    inp = load_inputs()
    text = (shellbench_root() / "docs" / "floor_concept.md").read_text(encoding="utf-8")
    p, k = rho_min_rule(text)
    r = rho_min(inp, text)
    assert r == pytest.approx(max(p, k * inp.f_t_pa / inp.f_y_pa / 100.0))
    assert 0.001 < r < 0.01  # a ratio of a few per mille, not a percentage


def test_frames_and_areas_on_a_flat_grid():
    xyz = flat_grid()
    e1, e2 = element_frames(xyz, N)
    assert np.allclose(e1, [1, 0, 0]) and np.allclose(e2, [0, 1, 0])
    a = element_areas(xyz, N)
    assert np.allclose(a, 1.0) and a.sum() == pytest.approx(16.0)


def test_element_areas_add_up_to_the_surface_area():
    net = square_network(10.0, 21, "edges")
    xyz = form_to_rise(net, 1.5)
    assert element_areas(xyz, 21).sum() == pytest.approx(surface_area(xyz, 21))


def test_tension_per_width_simple_states():
    xyz = flat_grid()
    e1, e2 = element_frames(xyz, N)
    t, s = 0.1, 2.0e6
    # uniform tension in x: T1 = s t, T2 = 0
    T = tension_per_width(faces(16, [s, 0, 0, 0, 0, 0]), e1, e2, t)
    assert np.allclose(T[:, 0], s * t) and np.allclose(T[:, 1], 0.0)
    # uniform compression: no steel
    assert np.allclose(tension_per_width(faces(16, [-s, -s, 0, 0, 0, 0]), e1, e2, t), 0.0)
    # pure shear: sigma + |tau| = tau in both directions
    assert np.allclose(tension_per_width(faces(16, [0, 0, 0, s, 0, 0]), e1, e2, t), s * t)
    # pure bending, +-s on the faces: tension block s t / 4
    f = np.zeros((16, 2, 6))
    f[:, 0, 0], f[:, 1, 0] = -s, s
    assert np.allclose(tension_per_width(f, e1, e2, t)[:, 0], s * t / 4, rtol=1e-3)


def test_symmetric_envelope_maps_one_corner_to_all_four_and_swaps_directions():
    m = (N - 1) // 2
    field = np.zeros((m * m, 2))
    field[1, 0] = 5.0  # element (J=0, I=1), direction x
    env = symmetric_envelope(field, N).reshape(m, m, 2)
    # x-steel at (0,1) by mirror goes to (0,2), (3,1), (3,2); transposed images carry it as y-steel
    for j, i in [(0, 1), (0, 2), (3, 1), (3, 2)]:
        assert env[j, i, 0] == 5.0
    for j, i in [(1, 0), (2, 0), (1, 3), (2, 3)]:
        assert env[j, i, 1] == 5.0
    assert env.sum() == 40.0


class _Res:
    """Stand-in for fe.CaseResult with only the face stresses."""

    def __init__(self, f):
        self.face_stress_pa = f


def test_take_off_of_a_stress_free_shell_is_the_minimum_steel():
    inp = load_inputs()
    xyz = flat_grid()
    t, rho, dens = 0.08, 0.002, 7850.0  # test inputs
    out = take_off(xyz, N, t, {"uls_gravity": _Res(np.zeros((16, 2, 6)))}, inp, rho, dens, 0.5)
    assert out.steel_kg == pytest.approx(2 * rho * t * 16.0 * dens)
    assert out.steel_kg == pytest.approx(out.steel_min_kg)
    assert out.demand_kg == 0.0 and out.zone_concrete_m3 == 0.0 and out.governing_case == ""


def test_take_off_counts_seismic_steel_and_zone_thickening():
    inp = load_inputs()
    xyz = flat_grid()
    t, rho, dens = 0.08, 0.002, 7850.0  # test inputs
    big = rho * t * inp.f_y_pa / t * 3.0  # uniform x tension at three times the minimum
    seis = faces(16, [big, 0, 0, 0, 0, 0])
    seis[0, :, 1] = -2.0 * inp.f_c_pa  # corner element crushed at twice f_c
    res = {"uls_gravity": _Res(np.zeros((16, 2, 6))), "uls_seismic_px": _Res(seis)}
    out = take_off(xyz, N, t, res, inp, rho, dens, 0.5)
    # symmetry: the x tension of +x becomes y tension of +y, so both directions carry 3 x minimum
    assert out.steel_kg == pytest.approx(3 * out.steel_min_kg)
    assert out.steel_from_seismic_kg == pytest.approx(2 * out.steel_min_kg)
    assert out.governing_case == "uls_seismic_px"
    assert out.zone_elements == 1 and out.zone_t_max_m == pytest.approx(2 * t)
    assert out.zone_concrete_m3 == pytest.approx(t * 1.0)


def test_factors_come_from_shellbench_in_place():
    import shellbench.carbon as sb

    f = load_factors()
    table = sb.read_factors(factors_path())
    v, unit = table[(f.set_name, sb.CONCRETE_GRADE)]
    assert unit == "kgCO2e/m3" and f.concrete_kgco2e_m3 == v
    v, unit = table[(f.set_name, sb.BAR_STEEL)]
    assert f.steel_kgco2e_kg == pytest.approx(v * sb.CONVERSIONS[unit][1])
    assert f.steel_density_kg_m3 == sb.STEEL_DENSITY_KG_M3


def test_band_corners_and_linear_carbon():
    corners = band_corners()
    assert set(corners) == {"c-s-", "c-s+", "c+s-", "c+s+"}
    assert corners["c+s-"] == (1 + FACTOR_BAND, 1 - FACTOR_BAND)
    f = load_factors()
    c = carbon_kgco2e(2.0, 100.0, f)
    assert c == pytest.approx(2.0 * f.concrete_kgco2e_m3 + 100.0 * f.steel_kgco2e_kg)
    assert carbon_kgco2e(2.0, 100.0, f, 1.25, 1.25) == pytest.approx(1.25 * c)
