"""Tests for design inputs, load cases, face stresses and the sizing loop."""

import numpy as np
import pytest

from shellform.fe import find_ccx, run_case
from shellform.formfind import corner_network_for_inset
from shellform.inputs import load_inputs, note_value, shellbench_root, spec_value
from shellform.sizing import THICKNESS_MIN_M, load_cases, thickness_grid
from shellform.strategies import seismic_mid_surface

needs_ccx = pytest.mark.skipif(find_ccx() is None, reason="CalculiX not on PATH")


def test_spec_value_reads_a_row():
    text = "| X7 | Concrete unit weight | 25 kN/m³ | Th §3.2.1 | |\n| X5 | Bars | **HRB400, fy = 360** | x | |\n"
    assert spec_value(text, "X7") == 25.0
    with pytest.raises(KeyError):
        spec_value(text, "L2")


def test_note_value_reads_a_row():
    text = "| ν_c | 0.25 | cl. 9.9, p. 1 |\n"  # test input, not a ShellBench value
    assert note_value(text, "ν_c") == 0.25
    with pytest.raises(KeyError):
        note_value(text, "G_c")


def test_poisson_ratio_comes_from_the_shellbench_note():
    text = (shellbench_root() / "notes" / "gb50010_design_values.md").read_text(encoding="utf-8")
    assert load_inputs().nu == note_value(text, "ν_c")


def test_inputs_come_from_shellbench():
    import shellbench.checks as sb_checks
    import shellbench.combinations as sb_comb

    inp = load_inputs()
    assert inp.f_c_pa == pytest.approx(sb_checks.FC_N_MM2 * 1e6)
    assert inp.gamma_eh == sb_comb.GAMMA_EH_CODE
    assert inp.sdl_pa > 0.0
    assert "[?]" not in inp.sources["nu"]


def test_thickness_grid_runs_from_tmin_to_span_over_50():
    grid = thickness_grid(10.0)
    assert grid[0] == pytest.approx(THICKNESS_MIN_M)
    assert grid[-1] == pytest.approx(0.20)
    assert np.allclose(np.diff(grid), 0.005)


def test_load_cases_follow_the_combinations():
    inp = load_inputs()
    cases, sls = load_cases(inp, 0.0)
    assert [c[0] for c in cases] == ["uls_gravity"]
    cases, _ = load_cases(inp, 0.3)
    name, acc, w = cases[1]
    assert acc[0] == pytest.approx(inp.gamma_eh * 0.3 * inp.g_m_s2)
    assert acc[2] == pytest.approx(-inp.gamma_eg * inp.g_m_s2)
    assert sls[0][2] == pytest.approx(-inp.g_m_s2)


@needs_ccx
def test_face_stress_matches_cantilever_plate(tmp_path):
    """Clamped plate under self-weight: root face stress and tip deflection."""
    n, length, t, rho, g, e = 21, 1.0, 0.02, 2500.0, 9.81, 3.0e10
    x, y = np.meshgrid(np.linspace(0, length, n), np.linspace(0, length, n))
    xyz = np.c_[x.ravel(), y.ravel(), np.zeros(n * n)]
    fixed = np.where(xyz[:, 0] < 1e-9)[0]
    r = run_case(xyz, n, fixed, t, e, 0.0, rho, (0, 0, -g), (0, 0, 0), workdir=tmp_path, clamp=True)
    q = rho * g * t
    assert r.max_uz_m == pytest.approx(q * length ** 4 / (8 * e * t ** 3 / 12), rel=5e-3)
    # first element row, centroid 0.05 m from the root; zone radius 0 keeps it in the check
    assert r.compression_support_pa == pytest.approx(6 * q * (length - 0.05) ** 2 / 2 / t ** 2, rel=5e-3)


@needs_ccx
def test_seismic_directions_are_equivalent(tmp_path):
    """+x stands for -x and +y on a strategy 2 corner shell (sizing.py docstring)."""
    net, grav, _ = corner_network_for_inset(10.0, 21, 1.5, 0.10)
    mid = seismic_mid_surface(grav, 0.3, 1.5)
    out = []
    for k, (ax, ay) in enumerate(((1, 0), (-1, 0), (0, 1))):
        r = run_case(mid, 21, net.fixed, 0.08, 3.25e10, 0.2, 2500.0,
                     (3.0 * ax, 3.0 * ay, -9.81), (0, 0, 0), workdir=tmp_path / str(k))
        out.append((r.buckling_factor, r.compression_pa))
    assert np.allclose(out[1], out[0], rtol=1e-3) and np.allclose(out[2], out[0], rtol=1e-3)
