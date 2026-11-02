"""Tests for steel, thickening and carbon of a sized shell (Day 5)."""

import numpy as np
import pytest

from shellform.fe import find_ccx, run_case, s8r_elements, surface_area
from shellform.formfind import corner_network_for_inset
from shellform.inputs import load_carbon_factors, load_inputs, rho_min_slab, shellbench_root
from shellform.quantities import (
    band_corners, carbon_kg, cheaper_strategy, covered_plan_area, element_areas, element_axes,
    element_compression, in_plane_stress, seismic_images, shell_quantities, tension_resultants)
from shellform.strategies import seismic_mid_surface

needs_ccx = pytest.mark.skipif(find_ccx() is None, reason="CalculiX not on PATH")

N = 5           # test grid, 2 x 2 S8R elements
F_C = 2.0e7     # test input, not a ShellBench value
F_Y = 4.0e8     # test input, not a ShellBench value
DENSITY = 8000.0  # test input, not a ShellBench value


def flat_plate(side=1.0, n=N):
    """Return a flat square grid in the xy plane."""
    g = np.linspace(0.0, side, n)
    x, y = np.meshgrid(g, g)
    return np.column_stack([x.ravel(), y.ravel(), np.zeros(n * n)])


def uniform_faces(sxx, top=None, syy=0.0, sxy=0.0, n=N):
    """Return face stresses on a plate: sxx on one face, top on the other."""
    n_el = ((n - 1) // 2) ** 2
    f = np.zeros((n_el, 2, 6))
    f[:, 0, 0], f[:, 1, 0] = sxx, sxx if top is None else top
    f[:, :, 1], f[:, :, 3] = syy, sxy
    return f


def plane(faces, n=N):
    """Return in-plane stresses of a flat test plate."""
    return in_plane_stress(faces, *element_axes(flat_plate(n=n), n))


def test_uniform_tension_gives_n_over_fy():
    q = shell_quantities(flat_plate(), N, 0.1, uniform_faces(1.0e7), None, F_C, F_Y, 0.0, DENSITY)
    # N = 1e7 Pa x 0.1 m = 1e6 N/m, A_s = 1e6 / 4e8 = 2.5e-3 m2/m, on 1 m2.
    assert q.steel_kg == pytest.approx(2.5e-3 * DENSITY)
    assert q.concrete_added_m3 == 0.0
    assert q.tension_governed_share == pytest.approx(1.0)


def test_pure_bending_gives_the_triangle_of_stress():
    t = tension_resultants(plane(uniform_faces(-6.0e6, 6.0e6)), 0.1, layers=2000)
    assert t[0, 0] == pytest.approx(0.5 * 6.0e6 * 0.05, rel=1e-3)
    assert t[0, 1] == 0.0


def test_resultants_do_not_depend_on_the_axes():
    # 45 degree rotation of a principal state (10, 2) MPa: sxx = syy = 6, sxy = 4.
    rotated = tension_resultants(plane(uniform_faces(6.0e6, syy=6.0e6, sxy=4.0e6)), 0.1)
    aligned = tension_resultants(plane(uniform_faces(1.0e7, syy=2.0e6)), 0.1)
    assert rotated == pytest.approx(aligned)


def test_rho_min_governs_when_tension_is_small_and_doubles_on_each_face():
    q = shell_quantities(flat_plate(), N, 0.1, uniform_faces(-1.0e6), None, F_C, F_Y, 0.002, DENSITY)
    assert q.steel_kg == pytest.approx(2 * 0.002 * 0.1 * DENSITY)
    assert q.steel_kg == pytest.approx(q.steel_kg_min_only)
    assert q.steel_kg_each_face == pytest.approx(2.0 * q.steel_kg)
    assert q.tension_governed_share == 0.0


def test_thickening_scales_with_the_stress_ratio():
    q = shell_quantities(flat_plate(), N, 0.1, uniform_faces(-3.0e7), None, F_C, F_Y, 0.0, DENSITY)
    assert q.concrete_added_m3 == pytest.approx(0.05)
    assert element_compression(uniform_faces(-3.0e7))[0] == pytest.approx(3.0e7)


def test_seismic_images_mirror_and_rotate():
    f = np.arange(4.0)  # elements (row, col): 0 1 / 2 3
    px, nx, py, ny = seismic_images(f)
    assert px.tolist() == [0, 1, 2, 3]
    assert nx.tolist() == [1, 0, 3, 2]
    assert py.tolist() == [0, 2, 1, 3]
    assert ny.tolist() == [1, 3, 0, 2]


def test_element_areas_sum_to_the_surface_area():
    xyz = flat_plate(side=2.0, n=9)
    xyz[:, 2] = 0.1 * xyz[:, 0] ** 2
    assert element_areas(xyz, 9).sum() == pytest.approx(surface_area(xyz, 9))
    assert covered_plan_area(xyz, 9) == pytest.approx(4.0)


def test_band_and_decision_rule():
    assert sorted(band_corners()) == [(0.75, 0.75), (0.75, 1.25), (1.25, 0.75), (1.25, 1.25)]
    assert cheaper_strategy(100.0, 94.0) == "seismic"
    assert cheaper_strategy(100.0, 96.0) == "no meaningful difference"
    assert cheaper_strategy(100.0, 106.0) == "gravity"


def test_rho_min_rule_reads_shellbench():
    text = "the larger of 0.5 % and 10 f_t / f_y"  # test input, not a ShellBench value
    assert rho_min_slab(2.0, 1.0, text) == pytest.approx(0.20)
    with pytest.raises(KeyError):
        rho_min_slab(2.0, 1.0, "no rule here")
    assert "the larger of" in (shellbench_root() / "docs" / "floor_concept.md").read_text(encoding="utf-8")
    inp = load_inputs()
    assert rho_min_slab(inp.f_t_pa, inp.f_y_pa) > 0.0


def test_carbon_factors_come_from_shellbench():
    f = load_carbon_factors()
    assert carbon_kg(2.0, 3.0, f) == pytest.approx(2.0 * f["concrete_kgco2e_m3"] + 3.0 * f["steel_kgco2e_kg"])
    assert carbon_kg(1.0, 0.0, f, concrete_scale=1.25) == pytest.approx(1.25 * f["concrete_kgco2e_m3"])
    assert carbon_kg(0.0, 1.0, f, steel_scale=0.75) == pytest.approx(0.75 * f["steel_kgco2e_kg"])


@needs_ccx
def test_minus_x_run_matches_the_mirrored_plus_x_field():
    n, span, sa = 21, 10.0, 0.4
    inp = load_inputs()
    net, grav, _ = corner_network_for_inset(span, n, 1.5, 0.10)
    mid = seismic_mid_surface(grav, sa, 1.5)
    e1, e2 = element_axes(mid, n)

    def field(sign):
        ax = sign * 1.4 * sa * 9.81
        r = run_case(mid, n, net.fixed, 0.09, inp.e_pa, inp.nu, inp.density_kg_m3,
                     (ax, 0.0, -1.3 * 9.81), (0.0, 0.0, -1000.0))
        return tension_resultants(in_plane_stress(r.face_stress_pa, e1, e2), 0.09)

    plus, minus = field(1.0), field(-1.0)
    mirrored = seismic_images(plus)[1]
    scale = plus.max()
    assert s8r_elements(n).shape[0] == plus.shape[0]
    assert np.abs(mirrored - minus).max() / scale < 0.02
