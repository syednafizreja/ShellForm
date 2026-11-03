"""Tests for the Day 6 pipeline: covered plan area, T1 mass, decision rules."""

import numpy as np
import pytest

from shellform.designs import CORNER_EDGE_INSET_RATIO, N_GRID, form
from shellform.fe import plan_area
from shellform.formfind import square_network
from shellform.pipeline import comparison, headline, period_with_sdl


def test_plan_area_of_a_flat_square_is_span_squared():
    net = square_network(10.0, 9, "edges")
    xyz = net.xyz.copy()
    xyz[:, 2] = 0.0
    assert plan_area(xyz, 9) == pytest.approx(100.0, rel=1e-12)


def test_plan_area_of_edge_and_corner_shells():
    case = {"span_m": 10.0, "rise_ratio": 0.15, "strategy": "gravity", "sa_g": 0.0}
    _, _, edges = form({**case, "supports": "edges"})
    _, _, corners = form({**case, "supports": "corners"})
    assert plan_area(edges, N_GRID) == pytest.approx(100.0, rel=1e-9)
    # Inset free edges (D3-1) leave the corner shell well under span squared.
    a = plan_area(corners, N_GRID)
    assert 100.0 * (1 - 4 * CORNER_EDGE_INSET_RATIO) < a < 100.0


def test_plan_area_scales_with_span_squared():
    case = {"rise_ratio": 0.15, "strategy": "gravity", "sa_g": 0.0, "supports": "corners"}
    _, _, a10 = form({**case, "span_m": 10.0})
    _, _, a20 = form({**case, "span_m": 20.0})
    assert plan_area(a20, N_GRID) == pytest.approx(4 * plan_area(a10, N_GRID), rel=1e-6)


def test_period_with_sdl_adds_mass():
    # Test inputs only, not design values.
    t = period_with_sdl(0.1, 2500.0, 0.1, 100.0, 100.0, 0.0, 9.81)
    assert t == pytest.approx(0.1)
    t2 = period_with_sdl(0.1, 2500.0, 0.1, 100.0, 100.0, 2452.5, 9.81)  # m_GE = m_concrete
    assert t2 == pytest.approx(0.1 * np.sqrt(2.0))


def _row(span, sup, strat, sa, c):
    r = {"span_m": span, "supports": sup, "rise_ratio": 0.15, "strategy": strat, "sa_g": sa,
         "carbon_gbt51366_kgco2e_m2": c}
    for k in ("c-s-", "c-s+", "c+s-", "c+s+"):
        r[f"carbon_kgco2e_m2_{k}"] = c
    return r


def test_comparison_and_headline():
    rows = []
    for sup in ("corners", "edges"):
        for sa in (0.0, 0.2):
            rows += [_row(10.0, sup, "gravity", sa, 100.0), _row(10.0, sup, "seismic", sa, 90.0 if sa else 100.0)]
    comp = comparison(rows)
    assert {r["verdict_central"] for r in comp if r["sa_g"] == 0.2} == {"seismic cheaper"}
    assert {r["verdict_central"] for r in comp if r["sa_g"] == 0.0} == {"no meaningful difference"}
    holds, cells = headline(comp)
    assert holds and len(cells) == 2
    rows[-1]["carbon_gbt51366_kgco2e_m2"] = 97.0  # edges, Sa 0.2, seismic: now within 5 %
    holds, cells = headline(comparison(rows))
    assert not holds and cells == [(10.0, "corners", 0.2)]
