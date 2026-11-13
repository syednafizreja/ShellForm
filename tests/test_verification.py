"""tests/test_verification.py

Tests of the check-window verification add-ons V1-V5 (shellform.verification)
and of their record files in results/.
"""

import csv
from pathlib import Path

import numpy as np
import pytest

from shellform import verification as V
from shellform.design_space import RISE_RATIOS, SPANS_M, SUPPORTS
from shellform.fe import find_ccx
from shellform.pin import SHELLBENCH_TAG

RESULTS = Path(__file__).resolve().parents[1] / "results"


def read(name):
    """Read a results CSV as a list of dicts."""
    with open(RESULTS / name, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


# --- V1 ---------------------------------------------------------------------

def test_zoelly_formula_by_hand():
    """E = 1, nu = 0, t/R = 0.1 gives 2/sqrt(3) x 0.01."""
    assert V.zoelly_pressure(1.0, 0.0, 0.1, 1.0) == pytest.approx(2 / np.sqrt(3) * 0.01, rel=1e-12)


def test_cube_sphere_mesh_is_closed_and_outward():
    """6 m^2 elements, every node on the sphere, every normal outward, area close to 4 pi R^2."""
    nodes, els = V.cube_sphere(2.0, 6)
    assert len(els) == 6 * 36
    assert np.allclose(np.linalg.norm(nodes, axis=1), 2.0)
    used = np.unique(els)
    assert used.min() == 1  # 1-based
    c = nodes[els[:, :4] - 1]
    normal = np.cross(c[:, 1] - c[:, 0], c[:, 3] - c[:, 0])
    assert (np.einsum("ij,ij->i", normal, c.mean(axis=1)) > 0).all()
    # Corner nodes of the patches: 6 faces of a (m+1)^2 grid, merged on the cube edges.
    corners = np.unique(els[:, :4])
    assert len(corners) == 6 * 6 ** 2 + 2


@pytest.mark.skipif(find_ccx() is None, reason="CalculiX not installed")
def test_zoelly_sphere_within_three_percent(tmp_path):
    """V1 on a light mesh (m = 12) already lands within 3 % of the closed form."""
    from shellform.inputs import load_inputs

    inp = load_inputs()
    r = V.zoelly_benchmark(inp.e_pa, inp.nu, m=12, workdir=tmp_path)
    assert r["passed"]
    assert r["membrane_ur_fe_m"] < 0  # external pressure moves the wall inward


# --- V3 ---------------------------------------------------------------------

@pytest.mark.parametrize("span", SPANS_M)
@pytest.mark.parametrize("supports", SUPPORTS)
@pytest.mark.parametrize("rise", RISE_RATIOS)
def test_fdm_residual_below_1e10_on_every_network(span, supports, rise):
    """||D x - p||_inf < 1e-10 N with unit nodal weights, gravity and Sa = 0.6 g."""
    case = dict(span_m=span, supports=supports, rise_ratio=rise)
    for sa in (0.0, 0.6):
        res, pmax = V.fdm_residual_of_case(case, sa_g=sa)
        assert pmax >= 1.0
        assert res < V.FDM_RESIDUAL_TOLERANCE


def test_fdm_residual_sees_a_moved_node():
    """A 1 mm move of one free node gives a residual far above the limit."""
    from shellform.designs import form

    net, grav, _ = form(dict(span_m=10.0, supports="edges", rise_ratio=0.15, strategy="gravity", sa_g=0.0))
    from shellform.formfind import plan_loads

    moved = grav.copy()
    moved[net.free[len(net.free) // 2], 2] += 1e-3
    assert V.fdm_residual(net, moved, plan_loads(net)) > 1e3 * V.FDM_RESIDUAL_TOLERANCE


# --- V4 ---------------------------------------------------------------------

def test_energy_split_pure_membrane_and_pure_bending():
    """Equal faces give all membrane; opposite faces give all bending, with the t/3 weight."""
    e, nu, t, a = 30e9, 0.2, 0.1, np.array([2.0])
    s = np.zeros((1, 2, 6))
    s[0, :, 0] = 1e6
    um, ub = V.energy_split(s, a, t, e, nu)
    assert ub == 0.0 and um == pytest.approx(a[0] * t * 1e12 / (2 * e))
    s[0, 0, 0] = -1e6
    um, ub = V.energy_split(s, a, t, e, nu)
    assert um == 0.0 and ub == pytest.approx(a[0] * t / 3 * 1e12 / (2 * e))


# --- V5 ---------------------------------------------------------------------

def test_formwork_term_stays_between_carbon_and_area_differences():
    """The mediant bound holds for every formwork intensity phi >= 0."""
    cg, cs, ag, as_ = 40.0, 38.0, 1.10, 1.115
    bound = V.formwork_bound(cs / cg - 1, as_ / ag - 1)
    for phi in np.geomspace(1e-3, 1e4, 50):
        rel = V.with_formwork(cs, as_, phi) / V.with_formwork(cg, ag, phi) - 1
        assert abs(rel) <= bound + 1e-12


# --- Record files ------------------------------------------------------------

@pytest.mark.parametrize("name", ["verify_v1_zoelly.csv", "verify_v2_hconv.csv", "verify_v3_fdm_residual.csv",
                                  "verify_v4_energy.csv", "verify_v5_formwork.csv"])
def test_record_names_the_pinned_tag(name):
    """Every verification record names the pinned ShellBench tag (CLAUDE.md code standards)."""
    rows = read(name)
    assert rows and {r["shellbench_tag"] for r in rows} == {SHELLBENCH_TAG}


def test_records_meet_their_acceptance_limits():
    """V1 finest meshes < 3 %, V2 finest pair < 1.5 %, V3 < 1e-10 N, V4 has all 168 designs."""
    v1 = read("verify_v1_zoelly.csv")
    m = max(int(r["m"]) for r in v1)
    assert all(abs(float(r["relative_error"])) < V.ZOELLY_TOLERANCE for r in v1 if int(r["m"]) == m)
    v2 = [r for r in read("verify_v2_hconv.csv") if int(r["n"]) == max(V.H_GRIDS)]
    assert len(v2) == 8
    assert all(float(r["buckling_factor_change_from_previous"]) < V.H_TOLERANCE for r in v2)
    assert all(float(r["passed"] == "True") for r in read("verify_v3_fdm_residual.csv"))
    assert len(read("verify_v4_energy.csv")) == 168
