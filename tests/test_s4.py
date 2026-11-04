"""Tests for test S4 (fallback): closed-form lean of a parabolic arch.

Pre-registration section 8 and the amendment of 4 Nov 2026: the full text of
Michiels & Adriaenssens (C&S 2018) was not available by 4 Nov, so S4 compares
ShellForm's solver with the closed-form lean of a parabolic arch under a
uniform horizontal acceleration. Pass: relative error below 1e-9.
"""

import numpy as np
import pytest

from shellform.checks import leaned_arch_reactions, leaned_parabola, support_reactions
from shellform.formfind import Network, form_to_rise

N_SEG = 40
TOL = 1e-9


def _arch(span):
    """Straight chain of N_SEG equal segments from x = 0 to x = span, ends pinned."""
    x = np.linspace(0.0, span, N_SEG + 1)
    xyz = np.column_stack([x, np.zeros_like(x), np.zeros_like(x)])
    edges = np.column_stack([np.arange(N_SEG), np.arange(1, N_SEG + 1)])
    return Network(xyz, edges, np.full(N_SEG, -1.0), np.array([0, N_SEG]),
                   np.arange(1, N_SEG), np.zeros(N_SEG, bool))


@pytest.mark.parametrize("span", [10.0, 20.0])
def test_s4_primary_case_matches_closed_form(span):
    """Rise-to-span 1/4 at 0.3 g (pre-registered case): nodes on the leaned parabola."""
    rise, sa = span / 4, 0.3
    net = _arch(span)
    s = net.xyz[:, 0].copy()
    form = form_to_rise(net, rise, sa_x=sa)
    x, z = leaned_parabola(span, rise, sa, s)
    assert np.hypot(form[:, 0] - x, form[:, 2] - z).max() / span < TOL


@pytest.mark.parametrize("span", [10.0, 20.0])
def test_s4_reactions_match_closed_form(span):
    """Thrusts differ by Sa W, the vertical reactions stay W / 2 each."""
    rise, sa = span / 4, 0.3
    net = _arch(span)
    form = form_to_rise(net, rise, sa_x=sa)
    r = support_reactions(form, net.edges, net.q, net.fixed)
    cf = leaned_arch_reactions(span, rise, sa, N_SEG, 1.0)
    w = N_SEG - 1.0
    assert abs(r[0, 0] - cf["h_left"]) / w < TOL
    assert abs(-r[1, 0] - cf["h_right"]) / w < TOL
    assert abs(r[0, 2] - cf["v_left"]) / w < TOL and abs(r[1, 2] - cf["v_right"]) / w < TOL
    assert r[:, 0].sum() == pytest.approx(-sa * w, rel=1e-12)  # reactions balance Sa W


def test_arch_leans_into_the_load():
    """For Sa > 0 in +x the compression line leans to -x, by Sa f at the crown."""
    span, rise, sa = 10.0, 2.5, 0.3
    net = _arch(span)
    form = form_to_rise(net, rise, sa_x=sa)
    crown = N_SEG // 2
    assert form[crown, 0] == pytest.approx(span / 2 - sa * rise, abs=1e-12)
    assert form[crown, 2] == pytest.approx(rise, abs=1e-12)


def test_leaned_parabola_without_load_is_the_gravity_parabola():
    """Sa = 0 gives z = 4 f s (L - s) / L^2 and x = s."""
    s = np.linspace(0.0, 8.0, 9)
    x, z = leaned_parabola(8.0, 2.0, 0.0, s)
    assert np.allclose(x, s) and z.max() == pytest.approx(2.0)
