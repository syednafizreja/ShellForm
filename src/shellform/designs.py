"""Build the network and mid-surface of one design case.

Moved here from scripts/day04_size_10m.py on 2 Nov so that the Day 4 sizing
and the Day 5 steel take-off build exactly the same forms.
"""

from shellform.formfind import corner_network_for_inset, form_to_rise, square_network
from shellform.strategies import seismic_mid_surface

N_GRID = 41                     # pre-registration section 3 (41 x 41 network)
CORNER_EDGE_INSET_RATIO = 0.10  # decision D3-1 [J]


def grid_n(case):
    """Return the network size of one case: case["grid_n"] if given, else N_GRID.

    The design space has no grid_n key, so every design uses the
    pre-registered 41 x 41 network; the mesh sensitivity run (Day 9,
    pre-registration section 7) adds grid_n = 61.
    """
    return int(case.get("grid_n", N_GRID))


def form(case):
    """Return (network, gravity form, mid-surface) for one design case.

    Args:
        case: Dict with span_m, rise_ratio, supports, strategy and sa_g
            (shellform.design_space), and optionally grid_n (see grid_n).

    Returns:
        (network, gravity form nodes (n*n, 3), mid-surface nodes (n*n, 3)) [m].
    """
    span, rise = case["span_m"], case["rise_ratio"] * case["span_m"]
    n = grid_n(case)
    if case["supports"] == "corners":
        net, grav, _ = corner_network_for_inset(span, n, rise, CORNER_EDGE_INSET_RATIO)
    else:
        net = square_network(span, n, "edges")
        grav = form_to_rise(net, rise)
    mid = grav.copy() if case["strategy"] == "gravity" else seismic_mid_surface(grav, case["sa_g"], rise)
    return net, grav, mid
